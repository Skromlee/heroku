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
    # if action == 'view-house-type':
    #     res = view_type(req)
    if action == 'view-house-details' or action == 'house-details':
        res = view_details(req)
    else:
        log.error('Unexpected action.')

    print('Action: ' + action)
    print('Response: ' + res)
    
    # return make_response('./test.json')
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

# combo_set_resp = {
#     "type-a": "บ้านประเภท A จะมีราคาประมาณ 7 - 11 ล้านบาท โดยจะมีพื้นที่ใข้สอยโดยประมาณอยู่ที่ 300 ตร.ม. โดยเมื่อซื้อกับเราจะแถม แอร์ทุกห้อง รวมทั้ง ฟรีค่าโอน และ จดจำนอง",
#     "type-b": "บ้านประเภท B จะมีราคาประมาณ 1 - 3 ล้านบาท โดยจะมีพื้นที่ใข้สอยโดยประมาณอยู่ที่ 110 - 130 ตร.ม. โดยเมื่อซื้อกับเราจะแถม แอร์ทุกห้อง รวมทั้ง ฟรีค่าโอน และ จดจำนอง",
#     "type-c": "บ้านประเภท C จะมีราคาประมาณ 4 - 7 ล้านบ้าน โดยจะมีพื้นที่ใข้สอยโดยประมาณอยู่ที่ 180 - 220 ตร.ม. โดยเมื่อซื้อกับเราจะแถม แอร์ทุกห้อง รวมทั้ง ฟรีค่าโอน และ จดจำนอง"
# }

# 4XXX = บ้านเดี่ยว


house_details_des = {
    4777:   "รหัสทรัพย์สิน 4777 เป็นบ้านเดี่ยว 2 ชั้นแบบ Modern นะคะ มีทั้งหมด 3 ห้องนอน 3 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 183 ตร.ม.ค่ะ ราคาขายอยู่ที่ 8,900,000 บาทค่ะ",
    4888:   "รหัสทรัพย์สิน 4888 เป็นบ้านเดี่ยว 4 ชั้นแบบ Luxury นะคะ มีทั้งหมด 4 ห้องนอน 5 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 403 ตร.ม.ค่ะ ราคาขายอยู่ที่ 12,999,000 บาทค่ะ",
    4999:   "รหัสทรัพย์สิน 4999 เป็นบ้านเดี่ยว 2 ชั้นแบบ Ancient นะคะ มีทั้งหมด 4 ห้องนอน 5 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 350 ตร.ม.ค่ะ ราคาขายอยู่ที่ 10,850,000 บาทค่ะ",
    2111:   "รหัสทรัพย์สิน 2111 เป็นบ้านทาวเฮ้าท์ 2 ชั้นแบบ Ancient นะคะ มีทั้งหมด 3 ห้องนอน 3 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 183 ตร.ม.ค่ะ ราคาขายอยู่ที่ 8,900,000 บาทค่ะ",
    2222:   "รหัสทรัพย์สิน 2222 เป็นบ้านทาวเฮ้าท์ 2 ชั้นแบบ Modern นะคะ มีทั้งหมด 3 ห้องนอน 3 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 183 ตร.ม.ค่ะ ราคาขายอยู่ที่ 8,900,000 บาทค่ะ",
    2333:   "รหัสทรัพย์สิน 2333 เป็นบ้านทาวเฮ้าท์ 2 ชั้นแบบ Mix นะคะ มีทั้งหมด 3 ห้องนอน 3 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 183 ตร.ม.ค่ะ ราคาขายอยู่ที่ 8,900,000 บาทค่ะ",
    6333:   "รหัสทรัพย์สิน 6333 เป็นบ้านทาวเฮ้าท์ 2 ชั้นแบบ Mix นะคะ มีทั้งหมด 3 ห้องนอน 3 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 183 ตร.ม.ค่ะ ราคาขายอยู่ที่ 8,900,000 บาทค่ะ",
    6444:   "รหัสทรัพย์สิน 6444 เป็นบ้านทาวเฮ้าท์ 2 ชั้นแบบ Mix นะคะ มีทั้งหมด 3 ห้องนอน 3 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 183 ตร.ม.ค่ะ ราคาขายอยู่ที่ 8,900,000 บาทค่ะ",
    6555:   "รหัสทรัพย์สิน 6555 เป็นบ้านทาวเฮ้าท์ 2 ชั้นแบบ Mix นะคะ มีทั้งหมด 3 ห้องนอน 3 ห้องน้ำ มีพื้นที่ใช้สอยทั้งหมด 183 ตร.ม.ค่ะ ราคาขายอยู่ที่ 8,900,000 บาทค่ะ"
}

# def view_type(req):
#     parameters = req.get('queryResult').get('parameters')
#     combo_set = parameters.get('combo-set')
#     return combo_set_resp[combo_set]

def view_details(req):
    parameters = req.get('queryResult').get('parameters')
    pro_id = parameters.get('pro_id')
    return house_details_des[pro_id]

if __name__ == '__main__':
    app.run()