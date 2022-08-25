from flask import render_template
from flask_mail import Message
from scanaudit import db, mail
from scanaudit.models import( 
    Orders, 
    OrderScans,
    OrderPackageItems)
from scanaudit.config import config
from datetime import datetime, timedelta

import os
import csv
import xlsxwriter


def check_last_audit():
    last_audit = None
    # Check if any previous audit has been conducted
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "lastaudit.txt")
        
        if os.path.exists(file_path) and os.stat(file_path).st_size > 0:
            with open(file_path, 'r') as f:
                last_line = f.readlines()[-1]
                last_line = last_line.strip('\n')
                if len(last_line) > 0:
                    last_audit = datetime.strptime(last_line.strip('\n'), "%Y-%m-%d %H:%M:%S.%f")
                return last_audit
    except Exception as e:
        print(e)
    return last_audit

# Return list of files with scancodes to be scanned
def generate_scan_file_list(last_audit):
    dir_path = config.FILE_DIR
    file_list = []
    try:
        for file in os.listdir(dir_path):
            if 'PackagesReceived' in file and file.endswith(".csv"):
                scan_file = os.path.join(dir_path, file)
                lmt = os.path.getmtime(scan_file)
                modified = datetime.fromtimestamp(lmt)
                
                if last_audit is not None:
                    if modified >= last_audit:
                        file_list.append(scan_file)
                else:
                    file_list.append(scan_file)
    except Exception as e:
        print(e)
    return file_list

def generate_master_list_scan_codes(file_list):
    scan_codes = {}
    try:
        for file in file_list:
            with open(file) as csvfile: 
                csvreader =  csv.reader(csvfile, delimiter=',')
                header = next(csvreader)
                for line in csvreader:
                    scan_codes[line[0]] = line[1]
    except Exception as e:
        print(e)
    return scan_codes

# Cross-reference scan codes 
def get_unscanned_codes(master_scan_codes): 
    scan_codes = master_scan_codes.keys()
    db_scan_codes = db.session.query(OrderScans.SCANcode)
    db_scan_codes = db_scan_codes.filter(
        OrderScans.SCANlocation == 'R' 
    ).all()
    db_scan_codes = [r._asdict() for r in db_scan_codes]
    order_scans = [d['SCANcode'] for d in db_scan_codes]
    unscanned_codes = list(set(scan_codes) - set(order_scans))
    return unscanned_codes

# Get OrderTrackingID for packages without scan codes
def get_order_tracking_ids():
    unscanned_orders = {}
    try:
        threshold =  datetime.today() - timedelta(days=14)
        threshold = threshold.date()
        db_orders = db.session.query(Orders.OrderTrackingID, OrderPackageItems.RefNo)
        db_orders = db_orders.join(OrderPackageItems, Orders.OrderTrackingID == OrderPackageItems.OrderTrackingID).all()
        db_orders = [r._asdict() for r in db_orders]
        unscanned_orders = {}
        for order in db_orders:
            k = order['RefNo']
            v = order['OrderTrackingID']
            unscanned_orders[k] = v
    except Exception as e: 
        print(e)
    return unscanned_orders

# Generate audit report file
def generate_audit_report(master_scan_list, order_package_items, unscanned_codes):
    today = datetime.now()
    today = today.strftime("%m_%d_%y_%H_%M_%S")
    file_name = 'Audit_Report-' + today + '.xlsx'

    if len(unscanned_codes) > 0:
        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet()

        headers = ['OrderTrackingID', 'ScanCode', 'TimeStamp']
        for x in range(len(headers)):
            worksheet.write(0, x, headers[x])
        
        for idx, scan in enumerate(unscanned_codes):
            if scan in order_package_items: 
                worksheet.write(idx+1, 0, order_package_items[scan])
            else:
                worksheet.write(idx+1, 0, 'None')
            worksheet.write(idx+1, 1, scan)
            worksheet.write(idx+1, 2, master_scan_list[scan])

        workbook.close()

        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "lastaudit.txt")
        append_write = 'w' 
        if os.path.exists(file_path):
            append_write = 'a' # append if already exists
            
        with open(file_path, append_write) as f:
            f.write(str(datetime.now()))
            f.write('\n')

        subject = 'Scan Audit - ' + today
        msg = Message(
                    sender=str(config.MAIL_DEFAULT_SENDER),
                    subject=subject,
                    recipients = config.RECIPIENTS
                )
        msg.body = 'Find attached the scan audit report in the email'
        file = open(file_name, 'rb')
        msg.attach(file_name, '	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', file.read())
        mail.send(msg)
        return render_template('success.html')
    else:
        return 'Nothing was found'

