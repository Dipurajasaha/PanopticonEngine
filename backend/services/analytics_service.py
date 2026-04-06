from sqlalchemy.orm import Session
from sqlalchemy import func
import models.db_models as db_models

def get_global_analytics(db: Session):
    totals = db.query(
        db_models.FinanceRecord.record_type,
        func.sum(db_models.FinanceRecord.amount).label("total")
    ).filter(
        db_models.FinanceRecord.is_deleted == False
    ).group_by(db_models.FinanceRecord.record_type).all()

    total_income = 0.0
    total_expense = 0.0

    for record_type, total in totals:
        if record_type.lower() == "income":
            total_income = total or 0.0
        elif record_type.lower() == "expense":
            total_expense = total or 0.0
    
    net_balance = total_income - total_expense

    category_data = db.query(
        db_models.FinanceRecord.category,
        func.sum(db_models.FinanceRecord.amount).label("total")
    ).filter(
        db_models.FinanceRecord.is_deleted == False,
    ).group_by(db_models.FinanceRecord.category).all()
    

    category_breakdown = [
        {"category": cat, "total_amount":amt or 0.0} for cat, amt in category_data    
    ]

    return {
        "total_income"      : total_income,
        "total_expense"     : total_expense,
        "net_balance" : net_balance,
        "category_breakdown" : category_breakdown,
    }