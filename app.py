from flask import Flask, jsonify, request
from peewee import *
from flask_restful import Api, Resource, reqparse
import datetime, socket
# import logging

db = 'gamerpg.db'
database = SqliteDatabase(db)

class BaseModel(Model):
	class Meta:
		database = database

class user(BaseModel):
	id_user = AutoField(primary_key=True)
	username = CharField(unique=True)
	password = CharField()

class pangkat(BaseModel):
	id_pangkat = AutoField(primary_key=True)
	nama_pangkat = CharField(unique=True)

class quest(BaseModel):
	id_quest = AutoField(primary_key=True)
	nama_quest = CharField(unique=True)

class karakter(BaseModel):
	id_karakter = AutoField(primary_key=True)
	id_user = ForeignKeyField(user)
	id_pangkat = ForeignKeyField(pangkat)
	id_quest = ForeignKeyField(quest)
	nickname = CharField(unique=True)

class item(BaseModel):
	id_item = AutoField(primary_key=True)
	nama_item = CharField(unique=True)
	point = IntegerField()

class karakter_item(BaseModel):
	id_karakter_item = AutoField(primary_key=True)
	id_item = ForeignKeyField(item)
	id_karakter = ForeignKeyField(karakter)

class maps(BaseModel):
	id_maps = AutoField(primary_key=True)
	nama_maps = CharField(unique=True)

class battle(BaseModel):
	id_battle = AutoField(primary_key=True)
	id_maps = ForeignKeyField(maps)
	id_karakter = ForeignKeyField(karakter)

class chat(BaseModel):
	id_chat = AutoField(primary_key=True)
	id_user1 = ForeignKeyField(user)
	id_user2 = ForeignKeyField(user)
	isi_chat = TextField()

class log(BaseModel):
	id_log = AutoField(primary_key=True)
	id_user = ForeignKeyField(user)
	waktu_login = DateTimeField()
	ip_address = TextField()

def create_tables():
	with database:
		database.create_tables([user, pangkat, quest, karakter, item, karakter_item, maps, battle, chat, log])

app = Flask(__name__)
api = Api(app)

def generate_datetime():
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	now = datetime.datetime.strptime(now,('%Y-%m-%d %H:%M:%S'))
	return now

# @app.before_request
# def log_request_info():
# 	logging.basicConfig(filename='log.log',level=logging.INFO)

class signup(Resource):
	def post(self):
		datas = request.json
		if datas is None:
			return jsonify({'hasil':'json anda kosong'})
		else:
			try:
				d_username = datas['username']
				print('username ok')
				try:
					d_password = datas['password']
					print('password ok')
					try:
						user.create(username=d_username,password=d_password)
						return jsonify({'hasil':'user created'})
					except IntegrityError:
						return jsonify({'hasil':'already exist'})
				except KeyError:
					return jsonify({'hasil':'password gada'})
			except KeyError:
				return jsonify({'hasil':'username gada'})


class coba(Resource):
	def get(self):
		
		list_data = []
		datas = user.select()
		for i in datas:
			u = {}
			u['username'] = i.username
			u['password'] = i.password
			list_data.append(u)
		
		list_data_karakter = []
		datas2 = karakter.select().join(user).switch(karakter).join(pangkat).switch(karakter).join(quest)
		print(datas2)
		for i in datas2:
			u = {}
			u['user'] = i.id_user.username
			u['pangkat'] = i.id_pangkat.nama_pangkat
			u['misi'] = i.id_quest.nama_quest
			u['nickname'] = i.nickname
			list_data_karakter.append(u)

		datasend = {}
		datasend['user'] = list_data
		datasend['karakter'] = list_data_karakter

		return jsonify({'hasil':datasend})


class req_maps(Resource):
	def get(self):
		datas = maps.select()
		lis_maps = []
		for i in datas:
			u = {}
			u['id_maps'] = i.id_maps
			u['nama_maps'] = i.nama_maps
			lis_maps.append(u)
		return jsonify({'hasil':lis_maps})

	def post(self):
		datas = request.json
		if datas is None:
			return jsonify({'hasil': 'Data yang anda kirim kosong'})
		else:
			try:
				d_nama_maps = datas['nama_maps']
				try:
					maps.create(nama_maps = d_nama_maps)
					response = jsonify({'hasil':'Maps Berhasil dibuat'})
					response.status_code = 201
					return response
				except IntegrityError:
					response = jsonify({'hasil': 'Maps already exist'})
					response.status_code = 409
					return response
			except KeyError:
				response = jsonify({'hasil':'nama_maps kosong'})
				response.status_code = 400
				return response

	def put(self):
		datas = request.json
		if datas is None:
			return jsonify({'hasil': 'Data yang anda kirim kosong'})
		else:
			try:
				d_nama_maps = datas['nama_maps']
				try:
					d_id_maps = datas['id_maps']
					try:
						d_maps = maps.update(nama_maps=d_nama_maps).where(maps.id_maps == int(d_id_maps))
						d_maps.execute()
						return jsonify({'hasil':'Maps Berhasil diubah'})
					except IntegrityError:
						return jsonify({'hasil': 'Maps already exist'})
				except KeyError:
					return jsonify({'hasil':'id_maps kosong'})
			except KeyError:
				return jsonify({'hasil':'nama_maps kosong'})

	def delete(self):
		datas = request.json
		if datas is None:
			return jsonify({'hasil':'Data kosong'})
		else:
			try:
				d_id_maps = datas['id_maps']
				d_maps = maps.delete().where(maps.id_maps == int(d_id_maps))
				d_maps.execute()
				return jsonify({'hasil':'Maps Berhasil Dihapus'})
			except KeyError:
				return jsonify({'hasil':'id_maps kosong'})


class req_pangkat(Resource):
	def get(self):
		datas = pangkat.select()
		lis_pangkat = []
		for i in datas:
			u = {}
			u['id_pangkat'] = i.id_pangkat
			u['nama_pangkat'] = i.nama_pangkat
			lis_pangkat.append(u)
		return jsonify({'hasil':lis_pangkat})

	def post(self):
		datas = request.json
		if datas is None:
			return jsonify({'hasil':'json kosong'})
		else:
			try:
				d_nama_pangkat = datas['nama_pangkat']
				try:
					pangkat.create(nama_pangkat=d_nama_pangkat)
					response = jsonify({'hasil':'pangkat created'})
					response.status_code = 201
					return response
				except IntegrityError:
					response = jsonify({'hasil':'pangkat already exist'})
					response.status_code = 409
					return response
			except KeyError:
				response = jsonify({'hasil':'nama_pangkat gada'})
				response.status_code = 400
				return response

	def put(self):
		datas = request.json
		if datas is None:
			return jsonify({'hasil':'json kosong'})
		else:
			try:
				try:
					d_id_pangkat = int(datas['id_pangkat'])
					try:
						d_nama_pangkat = datas['nama_pangkat']
						try:
							d_pangkat = pangkat.update(nama_pangkat=d_nama_pangkat).where(pangkat.id_pangkat == int(d_id_pangkat))
							d_pangkat.execute()
							return jsonify({"hasil":"pangkat Berhasil diubah"})
						except IntegrityError:
							return jsonify({"hasil":"pangkat already exist"})
					except KeyError:
						return jsonify({'hasil':'nama_pangkat gada'})
				except ValueError:
					return jsonify({'hasil':"id_pangkat harus integer"})
			except KeyError:
				return jsonify({'hasil':'id_pangkat gada'})

	def delete(self):
		datas = request.json
		if datas is None:
			return jsonify({'hasil':"json gada"})
		else:
			try:
				try:
					d_id_pangkat = int(datas['id_pangkat'])
					d_pangkat = pangkat.delete().where(pangkat.id_pangkat == d_id_pangkat)
					d_pangkat.execute()
					return jsonify({"hasil":"Pangkat berhasil Dihapus"})
				except ValueError:
					return jsonify({"hasil":"id_pangkat harus integer"})
			except KeyError:
				return jsonify({"hasil":"id_pangkat gada"})

class req_quest(Resource):
	def get(self):
		datas = quest.select()
		lis_quest = []
		for i in datas:
			u = {}
			u['id_quest'] = i.id_quest
			u['nama_quest'] = i.nama_quest
			lis_quest.append(u)
		return jsonify({'hasil':lis_quest})

	def post(self):
		datas = request.json
		if datas is None:
			return jsonify({'hasil':'json kosong'})
		else:
			try:
				d_nama_quest = datas['nama_quest']
				try:
					quest.create(nama_quest = d_nama_quest)
					response = jsonify({'hasil':'quest created'})
					response.status_code = 201
					return response
				except IntegrityError:
					response = jsonify({"hasil":"quest already exist"})
					response.status_code = 409
					return response
			except KeyError:
				response = jsonify({'hasil':'nama_quest gada'})
				response.status_code = 400
				return response

	def put(self):
		datas = request.json
		if datas is None:
			return jsonify({"hasil":"json kosong"})
		else:
			try:
				d_nama_quest = datas['nama_quest']
				try:
					d_id_quest = int(datas['id_quest'])
					try:
						d_quest = quest.update(nama_quest = d_nama_quest).where(quest.id_quest == d_id_quest)
						d_quest.execute()
						return jsonify({"hasil":"quest Berhasil diubah"})
					except:
						return jsonify({"hasil":"gagal"})
				except:
					return jsonify({"hasil":"id_quest invalid"})
			except KeyError:
				return jsonify({"hasil":"nama_quest gada"})

	def delete(self):
		datas = request.json
		if datas is None:
			return jsonify({"hasil":"data invalid"})
		else:
			try:
				d_id_quest = int(datas['id_quest'])
				try:
					d_quest = quest.delete().where(quest.id_quest == d_id_quest)
					d_quest.execute()
					return jsonify({"hasil":"quest berhasil Dihapus"})
				except:
					return jsonify({"hasil":"gagal hapus"})
			except:
				return jsonify({"hasil":"id_quest invalid"})

class req_item(Resource):
	def get(self):
		datas = item.select()
		lis_item = []
		for i in datas:
			u = {}
			u['id_item'] = i.id_item
			u['nama_item'] = i.nama_item
			u['point'] = i.point
			lis_item.append(u)
		return jsonify({'hasil':lis_item})

	def post(self):
		datas = request.json
		if datas is None:
			return jsonify({'hasil':"data kosong"})
		else:
			try:
				d_nama_item = datas['nama_item']
				try:
					d_point = int(datas['point'])
					try:
						item.create(
							nama_item=d_nama_item,
							point = d_point)
						response = jsonify({"hasil":"item created"})
						response.status_code = 201
						return response
					except IntegrityError:
						response = jsonify({"hasil":"item sudah ada"})
						response.status_code = 409
						return response
				except:
					response = jsonify({"hasil":"point gada atau tidak int"})
					response.status_code = 400
					return response
			except KeyError:
				response = jsonify({"hasil":"nama_item gada"})
				response.status_code = 400
				return response

	def put(self):
		datas = request.json
		try:
			d_nama_item = datas["nama_item"]
			d_point = int(datas["point"])
			d_id_item = int(datas["id_item"])
			try:
				d_item = item.update(
					nama_item = d_nama_item,
					point = d_point).where(item.id_item == d_id_item)
				d_item.execute()
				response = jsonify({"hasil":"Berhasil diubah"})
				response.status_code = 201
				return response
			except:
				response = jsonify({"hasil":"item sudah dipakai"})
				response.status_code = 409
				return response
		except:
			response = jsonify({"hasil":"data invalid"})
			response.status_code = 400
			return response

	def delete(self):
		datas = request.json
		try:
			d_id_item = int(datas['id_item'])
			try:
				d_item = item.delete().where(item.id_item == d_id_item)
				d_item.execute()
				response = jsonify({"hasil":"Berhasil Dihapus"})
				response.status_code = 201
				return response
			except:
				response = jsonify({"hasil":"Error gagal Dihapus"})
				response.status_code = 400
				return response
		except:
			response = jsonify({"hasil":"id_item invalid"})
			response.status_code = 400
			return response

class login(Resource):
	def post(self):
		datas = request.json
		try:
			d_username = datas['username']
			try:
				d_password = datas['password']
				try:
					d_user = user.get((user.username == d_username)&(user.password == d_password))
					datas = {}
					datas['id_user'] = d_user.id_user
					response = jsonify({"hasil":datas})
					response.status_code = 200
					
					ipads = socket.gethostbyname(socket.gethostname())
					
					log.create(
						id_user = d_user.id_user,
						waktu_login = generate_datetime(),
						ip_address = ipads)

					return response
				except DoesNotExist:
					response = jsonify({"hasil":"username/password salah"})
					response.status_code = 400
					return response
			except KeyError:
				response = jsonify({"hasil":"password gada"})
				response.status_code = 400
				return response
		except KeyError:
			response = jsonify({"hasil":"username gada"})
			response.status_code = 400
			return response

class req_character(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument("id_user",type=int,required=True,help='Must Be Int and Not Empty')
		args = parser.parse_args()
		datas = karakter.select().join(pangkat) .where(karakter.id_user == args['id_user'])
		karakter_datas = []
		if datas.exists():
			for i in datas:
				u = {}
				u['id_karakter'] = i.id_karakter
				u['nickname'] = i.nickname
				u['level'] = i.id_pangkat.nama_pangkat
				karakter_datas.append(u)
		return jsonify({"hasil":karakter_datas})

	def post(self):
		datas = request.json
		try:
			d_idusr = int(datas['id_user'])
			try:
				d_user = user.get(user.id_user == d_idusr)
				try:
					d_id_pangkat = int(datas['id_pangkat'])
					try:
						d_pangkat = pangkat.get(pangkat.id_pangkat == d_id_pangkat)
						try:
							d_id_quest = int(datas['id_quest'])
							try:
								d_quest = quest.get(quest.id_quest == d_id_quest)
								try:
									d_nickname = datas['nickname']
									try:
										karakter.create(
											id_user = d_idusr,
											id_pangkat = d_id_pangkat,
											id_quest = d_id_quest,
											nickname = d_nickname)
										return jsonify({"hasil":"karakter Created"})
									except IntegrityError:
										response = jsonify({"hasil":"nickname already used"})
										response.status_code = 409
										return response
								except KeyError:
									response = jsonify({"hasil":"nickname gada"})
									response.status_code = 400
									return response
							except DoesNotExist:
								response = jsonify({"hasil":"quest invalid"})
								response.status_code = 410
								return response
						except KeyError:
							response = jsonify({"hasil":"id_quest gada"})
							response.status_code = 400
							return response
					except DoesNotExist:
						response = jsonify({"hasil":"pangkat invalid"})
						response.status_code = 410
						return response
				except KeyError:
					response = jsonify({"hasil":"id_pangkat gada"})
					response.status_code = 400
					return response
			except DoesNotExist:
				response = jsonify({"hasil":"user invalid"})
				response.status_code = 410
				return response
		except KeyError:
			response = jsonify({"hasil":"id_user gada"})
			response.status_code = 400
			return response

api.add_resource(coba, '/coba/')
api.add_resource(login, '/login/')
api.add_resource(signup, '/signup/')
api.add_resource(req_maps, '/maps/')
api.add_resource(req_item, '/items/')
api.add_resource(req_quest, '/quest/')
api.add_resource(req_pangkat, '/pangkat/')
api.add_resource(req_character, '/character/')

if __name__ == '__main__':
	create_tables()
	app.run(debug=True)