from flask import render_template, request, Blueprint
from scanaudit.api_func.audit import (
    check_last_audit, 
    generate_scan_file_list, 
    generate_master_list_scan_codes, 
    get_unscanned_codes,
    get_order_tracking_ids,
    generate_audit_report
)


main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')

@main.route("/report", methods=["GET", "POST"])
def get_report():
    last_audit = check_last_audit()    
    file_list = generate_scan_file_list(last_audit)
    master_scan_list = generate_master_list_scan_codes(file_list)
    unscanned_codes = get_unscanned_codes(master_scan_list)
    order_package_items = get_order_tracking_ids()
    return generate_audit_report(master_scan_list, order_package_items, unscanned_codes)
    
@main.route("/last-audit", methods=["GET", "POST"])
def get_last_audit_report():
    return {'data': check_last_audit()}
