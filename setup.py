import re
from flask import Flask, request, make_response, jsonify
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dateutil.parser import parse
import os

cred = credentials.Certificate('./kl888-88f79-firebase-adminsdk-7vr01-7101c2a832.json')
default_app = firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
log = app.logger

@app.route("/", methods=['POST'])
#Using post as a method

def webhook():
    req = request.get_json(silent=True, force=True)
    try:
        action = req.get('queryResult').get('action')
    except AttributeError:
        return 'json error'

    # Action Switcher
    if action == 'reservation.reservation-yes':
        res = create_reservation(req)
    if action == 'view-house-details' or action == 'house-details':
        res = view_details(req)
    else:
        log.error('Unexpected action.')

    print('Action: ' + action)
    print('Response: ' + res)
    
    return make_response(jsonify({'fulfillmentText': res}))


def create_reservation(req):
    parameters = req.get('queryResult').get('parameters')
    name = parameters.get('name')
    pro_id = parameters.get('pro_id')
    time = parse(parameters.get('time'))
    date = parse(parameters.get('date'))

    date_ref = db.collection(u'date').document(str(date.date()))
    date_ref.collection(u'reservations').add({
        u'name': name,
        u'pro_id': pro_id,
        u'time': date.replace(hour=time.hour, minute=time.minute)
    })
    return 'เรียบร้อยละค่า ขอบคุณนะคะที่ให้ความสำคัญกับเรา เดี๋ยวจะมีฝ่ายประชาสัมพันธติดต่อกลับไปนะครับ'

house_details_des = {
    #Type-A
    4777:   "รหัสทรัพย์สิน 4777 เป็นบ้านเดี่ยว 2 ชั้นแบบ Modern นะคะ มีทั้งหมด 3 ห้องนอน 3 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 183 ตร.ม.ค่ะ ราคาขายอยู่ที่ 8,900,000 บาทค่ะ",
    4888:   "รหัสทรัพย์สิน 4888 เป็นบ้านเดี่ยว 4 ชั้นแบบ Luxury นะคะ มีทั้งหมด 4 ห้องนอน 5 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 403 ตร.ม.ค่ะ ราคาขายอยู่ที่ 12,999,000 บาทค่ะ",
    4999:   "รหัสทรัพย์สิน 4999 เป็นบ้านเดี่ยว 2 ชั้นแบบ Ancient นะคะ มีทั้งหมด 4 ห้องนอน 5 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 350 ตร.ม.ค่ะ ราคาขายอยู่ที่ 10,850,000 บาทค่ะ",
    #Type-B
    2111:   "รหัสทรัพย์สิน 2111 เป็นทาวน์โฮม 3 ชั้นแบบ Ancient นะคะ มีทั้งหมด 4 ห้องนอน 4 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 230 ตร.ม.ค่ะ ราคาขายอยู่ที่ 7,830,000 บาทค่ะ",
    2222:   "รหัสทรัพย์สิน 2222 เป็นทาวน์โฮม 4 ชั้นแบบ Modern นะคะ มีทั้งหมด 4 ห้องนอน 5 ห้องน้ำ 2 ห้องนั่งเล่น มีพื้นที่ใช้สอยทั้งหมด 280 ตร.ม.ค่ะ ราคาขายอยู่ที่ 8,490,000 บาทค่ะ",
    2333:   "รหัสทรัพย์สิน 2333 เป็นทาวน์โฮม 3 ชั้นแบบ Mix นะคะ มีทั้งหมด 3 ห้องนอน 3 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 170 ตร.ม.ค่ะ ราคาขายอยู่ที่ 4,565,000 บาทค่ะ",
    #Type-C
    6333:   "รหัสทรัพย์สิน 6333 เป็นบ้านเดี่ยว 1 ชั้นแบบ Modern นะคะ มีทั้งหมด 4 ห้องนอน 5 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 280 ตร.ม.ค่ะ ราคาขายอยู่ที่ 7,450,000 บาทค่ะ",
    6444:   "รหัสทรัพย์สิน 6444 บ้านเดี่ยวเฮ้าส์เดอะฮัมบูร์ก 1 ชั้นแบบ Ancient นะคะ มีทั้งหมด 4 ห้องนอน 4 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 230 ตร.ม.ค่ะ ราคาขายอยู่ที่ 10,900,000 บาทค่ะ",
    6555:   "รหัสทรัพย์สิน 6555 บ้านเดี่ยว 1 ชั้นแบบ Modern นะคะ มีทั้งหมด 3 ห้องนอน 2 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 80 ตร.ม.ค่ะ ราคาขายอยู่ที่ 3,900,000 บาทค่ะ"
}

def view_details(req):
    parameters = req.get('queryResult').get('parameters')
    pro_id = parameters.get('pro_id')
    return house_details_des[pro_id]

if __name__ == '__main__':
    app.run()