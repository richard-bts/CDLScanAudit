from scanaudit import db


class Orders(db.Model):
    __tablename__ = "Orders"
    OrderTrackingID = db.Column(db.Integer, primary_key=True)
    PickupTargetFrom = db.Column(db.DateTime)
    Status = db.Column(db.String(1))
    ServiceID = db.Column(db.Integer)
    RouteID = db.Column(db.Integer)
    

class OrderScans(db.Model):
    __tablename__ = "OrderScans"
    OrderTrackingID = db.Column(db.Integer, primary_key=True)
    SCANcode = db.Column(db.String(200))
    SCANlocation = db.Column(db.String(1))
 

class OrderPackageItems(db.Model):
    __tablename__ = "OrderPackageItems"
    OrderTrackingID = db.Column(db.Integer, primary_key=True)
    PackageItemID = db.Column(db.Integer)
    RefNo = db.Column(db.String(200))

