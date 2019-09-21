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
from bson.objectid import ObjectId
import pandas as pd

app = Flask(__name__)
app.secret_key = 'zsjdfnegee#sd43afsfmni4n3432dsfnnh30djdh3h8hjej9k*'
# app.config["MONGO_URI"] = "mongodb://adminnawa:N4vva7ech@localhost:27017/hondadb"
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



################################################################################3


#REGISTER NEW CUSTOMER

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
		return jsonify(
				{
					'fbid':fb_id,
					'access_token':access_token,
					'status':200
				}
			)
	else:
		return jsonify({'message': 'Gagal Input'}), 200



#################################################################################3

#SHOW ALL CUSTOMER


@app.route('/customer')
def all_customers():
	customer = mongo.db.costumer.find()
	resp = customers_schema.jsonify(customer), 200
	return resp








#################################################################################3

#SEARCH CUSTOMER ALREADY REGISTERED

@app.route('/customerfind', methods=['POST']) 
def customer():
	search_customer = request.form.get('input_fbid')
	customer = mongo.db.costumer.find({'fbid':search_customer})
	result = []
	if customer is None:
		return jsonify({"message":"Data Not Found"}), 200
	else:
		for cs in customer:
			result.append(
					{
						'id':str(cs['_id']),
						'fbid':cs['fbid'],
						'name':cs['name'],
						'jk':cs['jk'],
						'no_telp':cs['no_telp'],
						'address':cs['address']
					}
				)
		access_token = create_access_token(identity=search_customer)
		return jsonify(
				{
					'result':result,
					'access_token':access_token,
					'status':200
				}
			)





#################################################################################3

#SHOW ALL PRODUCT


@app.route('/allproduct')
def all_product():
	products = mongo.db.product.find()
	result = []
	for produk in products:
		result.append(
				{
					'id': str(produk['_id']),
					'type': produk['type']
				}
			)
	resp = jsonify({'result':result,
					'status':200})
	return resp




#################################################################################3

#DELETE PRODUCT


@app.route('/deleteproduk', methods=['GET'])
def delete_product():
	tipe = request.form['int_type']
	delete = mongo.db.product.delete_one({'type': tipe})
	if delete:
		return jsonify('Success!')





#################################################################################3

#CHOOSE TYPE PRODUCT


@app.route('/chooseprdct', methods=['POST'])
@jwt_required
def get_product():
	search = request.form.get('input_type')
	product = mongo.db.product.find({'nl_key':search})
	result = []
	if product is None:
		return jsonify({"message": "Data not found"}), 200
	else:
		for produk in product:
			result.append(
					{
						'id': str(produk['_id']),
						'type': produk['type'],
						'color':produk['color']
					}
				)
		resp = jsonify({'result':result,
						'status':200})
		return resp









#################################################################################3

# CHOOSE COLOR

@app.route('/choosecolor', methods=['POST'])
@jwt_required
def get_product_color():
	search_type = request.form.get('input_type')
	search_color = request.form.get('input_color')
	product = mongo.db.product.find({'nl_key':search_type},{'color': {'$elemMatch': {'nl_key': search_color}}})
	if product is None:
		return jsonify({"message": "Color Not Found"}), 200
	else:
		return products_schema.jsonify(product),200




#################################################################################3


# SHOW COLORS

@app.route('/showcolor', methods=['POST'])
@jwt_required
def product_color():
	search_type = request.form['input_type']
	product = mongo.db.product.find({'nl_key':search_type})
	result = []
	if product is None:
		return jsonify({"message": "Color Not Found"}), 200
	else:
		for produk in product:
			result.append(
					{
						'id': str(produk['_id']),
						'type': produk['type'],
						'color': produk['color']
					}
				)
		return jsonify({'result':result}),200




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


# INSERT NEW COLOR

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

#ORDER A MOTORCYCLE

@app.route('/ordering', methods=['POST'])
# @jwt_required
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
		check_product = mongo.db.product.update({'_id':ObjectId(str(id_tipe)),'color.id_color':id_color},{'$inc':{'color.$.stock': -1}})
		print(check_product)
		return jsonify({
						 "message":"Order Success",
						 "status":200
						}
					)


# buat Object
# [{"color_name":"Blue"},{"color_name":"Red"}]
#################################################################################3
# FIND THE NEAREST DEALER



def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(a))

def closest(p, v):
    return distance(v['lat'],v['lon'],p['lat'],p['lon'])

@app.route('/getlatlon', methods=['GET'])
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
					'id':str(document['_id']),
					'dealer_name':document['dealer_name'],
					'address':document['address'],
					'lat':document['lat'],
					'lon':document['lon'],
					'distance': distance
				}
			)
		
	return jsonify({"locations": results})

#################################################################################3

# IMPORT CSV
@app.route('/upload', methods=['POST'])
def uploadExcel():
    df = pd.read_csv(request.files['file'],delimiter = ";", decimal=",")  # csv file which you want to import
    records_ = df.to_dict(orient='records')
    dict = {}
    for rec in records_:
        print(rec)
        gettype = mongo.db.product.count({'type':rec['type']})
        if gettype > 0:
         # for x in gettype:
         #  print(x.color, flush=True)
            print(gettype)
            print('if')
            mongo.db.product.update({'type':rec['type']},{'$push':{
					'color':
						{
							'id_color':uuid.uuid4(), 
							'color_name':rec['color_name'],
							'photo':rec['photo'],
							'nl_key':rec['nl_cl'],
							'stock':rec['stock']
						}
					}
				})
        else:
            dict['type'] = rec['type']
            dict['_id'] = ObjectId()
            dict['nl_key'] = rec['nl_key']
            dict['color'] = [
            	{
                  'id_color': uuid.uuid4(),
                  'color_name': rec['color_name'],
                  'photo': rec['photo'],
                  'nl_key': rec['nl_cl'],
                  'stock': rec['stock']
                }
            ]
            dict['price'] = rec['price']
            print('else')
            print(dict)
            mongo.db.product.insert(dict)
    return jsonify({"status": "true"})
	



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


