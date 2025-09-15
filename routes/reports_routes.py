from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime
from controllers.reports_controller import ReportsController
from models.user_models import UserRole
from utils.unified_auth import require_role_unified, get_current_user_or_superadmin

router = APIRouter()

@router.get("/categories")
async def get_report_categories():
    """Get available report categories"""
    return await ReportsController.get_report_categories()

@router.get("/categories/{category_id}/reports")
async def get_category_reports(category_id: str):
    """Get reports available for a specific category"""
    return await ReportsController.get_category_reports(category_id)

@router.get("/financial")
async def get_financial_reports(
    start_date: Optional[datetime] = Query(None, description="Start date for report"),
    end_date: Optional[datetime] = Query(None, description="End date for report"),
    branch_id: Optional[str] = Query(None, description="Filter by branch ID"),
    session: Optional[str] = Query(None, description="Filter by session"),
    class_filter: Optional[str] = Query(None, alias="class", description="Filter by class"),
    section: Optional[str] = Query(None, description="Filter by section"),
    fees_type: Optional[str] = Query(None, description="Filter by fees type"),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get comprehensive financial reports"""
    return await ReportsController.get_financial_reports(
        current_user, start_date, end_date, branch_id, session, class_filter, section, fees_type
    )

@router.get("/students")
async def get_student_reports(
    branch_id: Optional[str] = Query(None, description="Filter by branch ID"),
    course_id: Optional[str] = Query(None, description="Filter by course ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for report"),
    end_date: Optional[datetime] = Query(None, description="End date for report"),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get comprehensive student reports"""
    return await ReportsController.get_student_reports(
        current_user, branch_id, course_id, start_date, end_date
    )

@router.get("/coaches")
async def get_coach_reports(
    branch_id: Optional[str] = Query(None, description="Filter by branch ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for report"),
    end_date: Optional[datetime] = Query(None, description="End date for report"),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get comprehensive coach reports"""
    return await ReportsController.get_coach_reports(
        current_user, branch_id, start_date, end_date
    )

@router.get("/branches")
async def get_branch_reports(
    branch_id: Optional[str] = Query(None, description="Filter by specific branch ID"),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get comprehensive branch reports"""
    return await ReportsController.get_branch_reports(current_user, branch_id)

@router.get("/courses")
async def get_course_reports(
    branch_id: Optional[str] = Query(None, description="Filter by branch ID"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get comprehensive course reports"""
    return await ReportsController.get_course_reports(current_user, branch_id, category_id)

@router.get("/filters")
async def get_report_filters(
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get available filter options for reports"""
    return await ReportsController.get_report_filters(current_user)

# Individual financial report endpoints matching the reference image
@router.get("/financial/total-balance-fees-statement")
async def get_total_balance_fees_statement(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    branch_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get Total Balance Fees Statement report"""
    result = await ReportsController.get_financial_reports(
        current_user, start_date, end_date, branch_id
    )
    return {
        "report_type": "Total Balance Fees Statement",
        "data": result["financial_reports"]["total_balance_fees_statement"],
        "generated_at": result["generated_at"]
    }

@router.get("/financial/balance-fees-statement")
async def get_balance_fees_statement(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    branch_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get Balance Fees Statement report"""
    result = await ReportsController.get_financial_reports(
        current_user, start_date, end_date, branch_id
    )
    return {
        "report_type": "Balance Fees Statement",
        "data": result["financial_reports"]["balance_fees_statement"],
        "generated_at": result["generated_at"]
    }

@router.get("/financial/daily-collection-report")
async def get_daily_collection_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    branch_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get Daily Collection Report"""
    result = await ReportsController.get_financial_reports(
        current_user, start_date, end_date, branch_id
    )
    return {
        "report_type": "Daily Collection Report",
        "data": result["financial_reports"]["daily_collection_report"],
        "generated_at": result["generated_at"]
    }

@router.get("/financial/type-wise-balance-report")
async def get_type_wise_balance_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    branch_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get Type Wise Balance Report"""
    result = await ReportsController.get_financial_reports(
        current_user, start_date, end_date, branch_id
    )
    return {
        "report_type": "Type Wise Balance Report",
        "data": result["financial_reports"]["type_wise_balance_report"],
        "generated_at": result["generated_at"]
    }

@router.get("/financial/fees-statement")
async def get_fees_statement(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    branch_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get Fees Statement report"""
    result = await ReportsController.get_financial_reports(
        current_user, start_date, end_date, branch_id
    )
    return {
        "report_type": "Fees Statement",
        "data": result["financial_reports"]["fees_statement"],
        "generated_at": result["generated_at"]
    }

@router.get("/financial/total-fee-collection-report")
async def get_total_fee_collection_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    branch_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get Total Fee Collection Report"""
    result = await ReportsController.get_financial_reports(
        current_user, start_date, end_date, branch_id
    )
    return {
        "report_type": "Total Fee Collection Report",
        "data": result["financial_reports"]["total_fee_collection_report"],
        "generated_at": result["generated_at"]
    }

@router.get("/financial/other-fees-collection-report")
async def get_other_fees_collection_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    branch_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get Other Fees Collection Report"""
    result = await ReportsController.get_financial_reports(
        current_user, start_date, end_date, branch_id
    )
    return {
        "report_type": "Other Fees Collection Report",
        "data": result["financial_reports"]["other_fees_collection_report"],
        "generated_at": result["generated_at"]
    }

@router.get("/financial/online-fees-collection-report")
async def get_online_fees_collection_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    branch_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get Online Fees Collection Report"""
    result = await ReportsController.get_financial_reports(
        current_user, start_date, end_date, branch_id
    )
    return {
        "report_type": "Online Fees Collection Report",
        "data": result["financial_reports"]["online_fees_collection_report"],
        "generated_at": result["generated_at"]
    }

@router.get("/financial/balance-fees-report-with-remark")
async def get_balance_fees_report_with_remark(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    branch_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get Balance Fees Report With Remark"""
    result = await ReportsController.get_financial_reports(
        current_user, start_date, end_date, branch_id
    )
    return {
        "report_type": "Balance Fees Report With Remark",
        "data": result["financial_reports"]["balance_fees_report_with_remark"],
        "generated_at": result["generated_at"]
    }

@router.get("/financial/expense-report")
async def get_expense_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    branch_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get Expense Report (placeholder for future implementation)"""
    return {
        "report_type": "Expense Report",
        "data": {"message": "Expense reporting feature coming soon"},
        "generated_at": datetime.utcnow()
    }

@router.get("/financial/payroll-report")
async def get_payroll_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    branch_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get Payroll Report (placeholder for future implementation)"""
    return {
        "report_type": "Payroll Report",
        "data": {"message": "Payroll reporting feature coming soon"},
        "generated_at": datetime.utcnow()
    }

@router.get("/financial/income-report")
async def get_income_report(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    branch_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get Income Report"""
    result = await ReportsController.get_financial_reports(
        current_user, start_date, end_date, branch_id
    )
    return {
        "report_type": "Income Report",
        "data": {
            "total_income": result["financial_reports"]["total_balance_fees_statement"]["total_amount"],
            "monthly_breakdown": result["financial_reports"]["total_fee_collection_report"]
        },
        "generated_at": result["generated_at"]
    }
