from flask_pymongo import PyMongo
from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from datetime import datetime
from math import cos, asin, sqrt
from decimal import *
from heapq import nsmallest
import uuid
import csv


app = Flask(__name__)
app.secret_key = 'zsjdfnegee#sd43afsfmni4n3432dsfnnh30djdh3h8hjej9k*'
app.config["MONGO_URI"] = "mongodb://localhost:27017/hondadb"
# app.config['JWT_TOKEN_LOCATION'] = ['query_string']
app.config['JWT_SECRET_KEY'] = 'nndjbaskfu4k2ifapteldnsaiewreksdoertwt'

mongo = PyMongo(app)
ma = Marshmallow(app)
jwt = JWTManager(app)


###############################################################################3
class CustomerSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('fbid', 'name', 'jk', 'no_telp', 'address')


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

class ProductSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('type','nl_key', 'color', 'stok', 'price')


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

class DealerSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('dealer_name','address','lat','lon')


dealer_schema = DealerSchema()
dealers_schema = DealerSchema(many=True)

# master data produk,color,type, CRUD, import excel, validasi JK pria/wanita, nambah response return + model users , update stock, semua ID pake UUID versi 4,get produckt by UUID, JWT jangan di Params (di header),  #






################################################################################3


#REGISTER CUSTOMER SUCCESS 80%

''' Notes: Add Validasi gender & check fbid jika sudah terdaftar return jwt '''

@app.route('/register', methods=['POST'])
def add_customer():
	json = request.form
	fb_id = request.form['fbid']
	find_fbid = mongo.db.costumer.count({'fbid':fb_id})
	if find_fbid >= 1:
		return jsonify({'message':'fb_id Has allready use!!'})
	nama = json['name']
	jk = json['jk']
	if (jk != "L") and (jk != "P"):
		return jsonify({
			"message":"Gender must L or P",
			"status":500
			})
	alamat = json['address']
	no_telp = json['no_telp']
	data = mongo.db.costumer.insert(
			{'fbid': fb_id, 
			 'name': nama, 
			 'jk': jk,
			 'no_telp': no_telp,  
			 'address': alamat
			 }
			)
	if data and request.method == 'POST':
		access_token = create_access_token(identity=fb_id)
		return jsonify(access_token=access_token),200
	else:
		return jsonify({'message': 'Gagal Input'}), 200



#################################################################################3





@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
#################################################################################3


#SHOW ALL CUSTOMER 100%

''' Mengeluarkan semua data customer '''


@app.route('/customer')
def all_customers():
	customer = mongo.db.costumer.find()
	resp = customers_schema.jsonify(customer), 200
	return resp








#################################################################################3

#SEARCH CUSTOMER ALREADY REGISTERED SUCCESS 100%


''' Cari data customer '''

@app.route('/customerfind', methods=['GET']) 
def customer():
	search_customer = request.form.get('input_fbid')
	customer = mongo.db.costumer.find_one({'fbid':search_customer})
	if customer is None:
		return jsonify({"message":"Data Not Found"}), 200
	else:
		access_token = create_access_token(identity=search_customer)
		return jsonify(access_token=access_token),200


		








#################################################################################3

#SHOW ALL PRODUCT SUCCESS 100%


''' Menampilkan semua product '''

@app.route('/allproduct')
def all_product():
	products = mongo.db.product.find()
	resp = products_schema.jsonify(products)
	return resp




#################################################################################3





@app.route('/deleteproduk', methods=['GET'])
def delete_product():
	tipe = request.form['int_type']
	delete = mongo.db.product.delete_one({'type': tipe})
	if delete:
		return jsonify('Success!')





#################################################################################3

#PILIH TYPE PRODUCT SUCCESS 100%


''' Pilih product yang akan di order dengan input type '''
@app.route('/chooseprdct', methods=['GET'])
@jwt_required
def get_product():
	search = request.form.get('input_type')
	product = mongo.db.product.find({'nl_key':search})
	if product is None:
		return jsonify({"message": "Data not found"}), 200
	else:
		return products_schema.jsonify(product), 200









#################################################################################3

# CHOOSE COLOR SUCCESS 100%

''' Pilih warna setelah mendapatkan inputan type dan color yang diinginkan  '''

@app.route('/choosecolor', methods=['POST'])
@jwt_required
def get_product_color():
	search_type = request.form.get('input_type')
	search_color = request.form.get('input_color')
	product = mongo.db.product.find({'nl_key':search_type},{'color': {'$elemMatch': {'nl_key': search_color}}})
	if product is None:
		return jsonify({"message": "Color Not Found"}), 200
	else:
		return products_schema.jsonify( product),200






#################################################################################3


# SHOW COLORS


'''  '''
@app.route('/showcolor', methods=['GET'])
@jwt_required
def product_color():
	search_type = request.form.get('input_type')
	product = mongo.db.product.find({'nl_key':search_type})
	if product is None:
		return jsonify({"message": "Color Not Found"}), 200
	else:
		return products_schema.jsonify(product),200





#################################################################################3

# INSERT NEW PRODUCT
@app.route('/newproduct', methods=['POST'])
def insert_newproduct():
	data = request.form
	_id = uuid.uuid4()
	tipe = data['int_type']
	nl_key = data['int_nlt']
	id_color = uuid.uuid4()
	color_name = data['int_color']
	photo = data['int_photo']
	nl_keyc = data['int_nlc']
	stok = data['int_stok']
	price = data['int_price']

	insert = mongo.db.product.insert({
		'_id': _id,
		'type': tipe,
		'nl_key': nl_key,
		'color':[{
			'id_color': id_color,
			'color_name': color_name,
			'photo': photo,
			'nl_key':nl_keyc,
			'stock':stok,
		}],'price':price
		})
	if insert and request.method == 'POST':
		return jsonify({"message":"Success Fully!"}), 200
	
# 	new_p = mongo.db.product.find({'type':tipe,'nl_key':nl_type,'color':[{'id_color':id_color,'color_name':color_name,'nl_key':nl_color,'stok':stok}],'price':price})





#################################################################################3


# New Color

@app.route('/newcolor', methods=['POST'])
def add_newcolor():
	data = request.form
	tipe = data['type']
	find_type = mongo.db.product.count({'nl_key':tipe})
	if find_type == 0:
		return jsonify({'message':'type is None'})
	id_color = uuid.uuid4()
	color_name = data['color_name']
	photo = data['photo']
	nl_key = data['nl_key']
	stok = data['stock']
	insert = mongo.db.product.update({'nl_key':tipe},{'$push':
		{
		'color':
			{
				'id_color':id_color, 
				'color_name':color_name,
				'photo':photo,
				'nl_key':nl_key,
				'stock':stok
			}
		}
	})
	if insert is None and request.method == 'POST':
		return jsonify({"message":"Field Required"}), 200
	else:
		return jsonify({"message":"Success Fully!"}), 200










#################################################################################3

#ORDER A MOTORCYCLE 75%

@app.route('/ordering', methods=['POST'])
@jwt_required
def order():
	id_tipe = request.form.get('id_type')
	id_color = request.form.get('id_color')
	id_customer = request.form.get('fbid',None)
	if id_tipe and id_color and id_customer is None:
		return jsonify({"message":"Fields Required!"})
	tanggal = datetime.now()
	ordered = mongo.db.ordered.insert({'id_type':id_tipe, 'id_color':id_color, 'id_customer':id_customer, 'tanggal':tanggal})
	if ordered is None:
		return jsonify({'Fields Required'}), 200
	else:
		return jsonify({"message":"SUCCESS"}), 200



# buat Object
# [{"color_name":"Blue"},{"color_name":"Red"}]
#################################################################################3


# latlon 
def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(a))

def closest(p, v):
    return distance(v['lat'],v['lon'],p['lat'],p['lon'])

@app.route('/getlatlon', methods=['POST'])
def gelLatLong():
	form = request.form
	lat = float(form['lat'])
	lon = float(form['lon'])
	max_distance = 0.75

	tempDataList = mongo.db.dealer.find({})
	results = []
	v = {'lat': lat, 'lon': lon}
	for document in tempDataList:
		distance = closest(document, v)
		if(distance <= max_distance):
			results.append(
				{
					'dealer_name':document['dealer_name'],
					'address':document['address'],
					'lat':document['lat'],
					'lon':document['lon'],
					'distance': distance
				}
			)
		
	return jsonify({"locations": results})

#################################################################################3


# @app.route('/', methods=['POST'])
# def addNew

# @app.route('/upload', methods=['POST'])
# def uploadExcel():
# 	client = MongoClient()
#     df = pd.read_csv(request.files['files'])
#     records_ = df.to_dict(orient = 'records')
#     result = mongo.db.product.insert(records_)
#     return str(result)
# 	color = pd.read_csv(request.files['product'])
# 	type = {"type":{mongo.db.product.find("type")}, "color":{mongo.db.product.find("color")}}
# 	color_list = type.color
	



#################################################################################3
@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    return resp, 404


if __name__ == '__main__':
	app.run(debug=True, port="5500")




# NOTES :


'''
	Progress :


	Import Excel		=> 25%
	

	latlong				=> 75%


	CRUD Master			=> 65%


	Order				=> 85%

'''