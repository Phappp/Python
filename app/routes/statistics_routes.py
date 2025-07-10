from flask import Blueprint, render_template, session, redirect, url_for, flash, request, send_file
from app.controllers.statistics_controller import StatisticsController
from app.utils.decorators import login_required, role_required
from datetime import datetime

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/lecture/dashboard')
@login_required
@role_required('lecture')
def lecture_dashboard():
    """
    Dashboard thống kê cho lecture
    """
    stats = StatisticsController.get_lecture_dashboard_stats()
    recent_activity = StatisticsController.get_recent_activity_stats()
    
    if not stats:
        flash('Không thể tải dữ liệu thống kê', 'danger')
        return redirect(url_for('main.home'))
    
    return render_template('lecture/dashboard.html', 
                         stats=stats, 
                         recent_activity=recent_activity)

@statistics_bp.route('/lecture/course/<course_id>/progress')
@login_required
@role_required('lecture')
def course_progress(course_id):
    """
    Thống kê tiến độ cho một khóa học cụ thể
    """
    stats = StatisticsController.get_course_progress_stats(course_id)
    
    if not stats:
        flash('Không tìm thấy thông tin khóa học', 'danger')
        return redirect(url_for('statistics.lecture_dashboard'))
    
    return render_template('lecture/course_progress.html', stats=stats)

@statistics_bp.route('/lecture/export-report')
@login_required
@role_required('lecture')
def export_report():
    """
    Xuất báo cáo thống kê
    """
    format_type = request.args.get('format', 'excel')
    
    if format_type not in ['excel', 'pdf']:
        flash('Định dạng không được hỗ trợ', 'danger')
        return redirect(url_for('statistics.lecture_dashboard'))
    
    try:
        report_data = StatisticsController.export_statistics_report(format_type)
        
        if not report_data:
            flash('Không thể tạo báo cáo', 'danger')
            return redirect(url_for('statistics.lecture_dashboard'))
        
        if format_type == 'excel':
            filename = f'bao_cao_thong_ke_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            return send_file(
                report_data,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        elif format_type == 'pdf':
            filename = f'bao_cao_thong_ke_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            return send_file(
                report_data,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
            
    except Exception as e:
        flash(f'Lỗi khi xuất báo cáo: {str(e)}', 'danger')
        return redirect(url_for('statistics.lecture_dashboard'))

@statistics_bp.route('/lecture/recent-activity')
@login_required
@role_required('lecture')
def recent_activity():
    """
    Xem hoạt động gần đây
    """
    activity_stats = StatisticsController.get_recent_activity_stats()
    
    if not activity_stats:
        flash('Không thể tải dữ liệu hoạt động', 'danger')
        return redirect(url_for('statistics.lecture_dashboard'))
    
    return render_template('lecture/recent_activity.html', activity_stats=activity_stats) 