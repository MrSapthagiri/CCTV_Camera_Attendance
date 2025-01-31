import os
from datetime import datetime, timedelta
import pandas as pd
from database import db
from fpdf import FPDF
import matplotlib.pyplot as plt
import seaborn as sns

class ReportGenerator:
    def __init__(self):
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_csv_report(self, start_date=None, end_date=None, user_id=None):
        """Generate CSV report for attendance records"""
        try:
            # Get attendance records
            records = self._get_attendance_records(start_date, end_date, user_id)
            
            if not records:
                print("❌ No attendance records found for the specified period")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Generate filename
            filename = self._generate_filename("csv", start_date, end_date, user_id)
            filepath = os.path.join(self.reports_dir, filename)
            
            # Save to CSV
            df.to_csv(filepath, index=False)
            print(f"✅ CSV report generated: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error generating CSV report: {str(e)}")
            return None

    def generate_excel_report(self, start_date=None, end_date=None, user_id=None):
        """Generate Excel report with attendance records and statistics"""
        try:
            # Get attendance records
            records = self._get_attendance_records(start_date, end_date, user_id)
            
            if not records:
                print("❌ No attendance records found for the specified period")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Generate filename
            filename = self._generate_filename("xlsx", start_date, end_date, user_id)
            filepath = os.path.join(self.reports_dir, filename)
            
            # Create Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Write attendance records
                df.to_excel(writer, sheet_name='Attendance Records', index=False)
                
                # Generate and write statistics
                stats_df = self._generate_statistics(df)
                stats_df.to_excel(writer, sheet_name='Statistics', index=True)
                
                # Generate and write daily summary
                daily_summary = self._generate_daily_summary(df)
                daily_summary.to_excel(writer, sheet_name='Daily Summary', index=True)
            
            print(f"✅ Excel report generated: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error generating Excel report: {str(e)}")
            return None

    def generate_pdf_report(self, start_date=None, end_date=None, user_id=None):
        """Generate PDF report with attendance records and visualizations"""
        try:
            # Get attendance records
            records = self._get_attendance_records(start_date, end_date, user_id)
            
            if not records:
                print("❌ No attendance records found for the specified period")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            # Generate filename
            filename = self._generate_filename("pdf", start_date, end_date, user_id)
            filepath = os.path.join(self.reports_dir, filename)
            
            # Create PDF
            pdf = FPDF()
            
            # Add title page
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Attendance Report', 0, 1, 'C')
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
            
            # Add date range
            if start_date and end_date:
                pdf.cell(0, 10, f'Period: {start_date} to {end_date}', 0, 1, 'C')
            elif user_id:
                pdf.cell(0, 10, f'User ID: {user_id}', 0, 1, 'C')
            
            # Add statistics
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Statistics', 0, 1, 'L')
            pdf.set_font('Arial', '', 12)
            
            stats_df = self._generate_statistics(df)
            for idx, row in stats_df.iterrows():
                pdf.cell(0, 10, f'{idx}: {row[0]}', 0, 1, 'L')
            
            # Generate and add visualizations
            self._add_visualizations(pdf, df)
            
            # Add attendance records
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Attendance Records', 0, 1, 'L')
            
            # Add table headers
            pdf.set_font('Arial', 'B', 12)
            col_width = pdf.w / 4.5
            pdf.cell(col_width, 10, 'Date', 1, 0, 'C')
            pdf.cell(col_width, 10, 'Time', 1, 0, 'C')
            pdf.cell(col_width, 10, 'User ID', 1, 0, 'C')
            pdf.cell(col_width, 10, 'Name', 1, 1, 'C')
            
            # Add table data
            pdf.set_font('Arial', '', 12)
            for _, row in df.iterrows():
                pdf.cell(col_width, 10, str(row['date']), 1, 0, 'C')
                pdf.cell(col_width, 10, str(row['time']), 1, 0, 'C')
                pdf.cell(col_width, 10, str(row['user_id']), 1, 0, 'C')
                pdf.cell(col_width, 10, str(row['name']), 1, 1, 'C')
            
            # Save PDF
            pdf.output(filepath)
            print(f"✅ PDF report generated: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error generating PDF report: {str(e)}")
            return None

    def _get_attendance_records(self, start_date=None, end_date=None, user_id=None):
        """Get attendance records based on date range or user_id"""
        try:
            if user_id:
                # Get records for specific user
                return db.get_user_attendance(user_id)
            elif start_date and end_date:
                # Get records for date range
                return db.get_attendance_range(start_date, end_date)
            else:
                # Get all records
                return db.get_attendance()
                
        except Exception as e:
            print(f"❌ Error retrieving attendance records: {str(e)}")
            return []

    def _generate_statistics(self, df):
        """Generate statistics from attendance records"""
        stats = {
            'Total Records': len(df),
            'Unique Users': df['user_id'].nunique(),
            'Date Range': f"{df['date'].min()} to {df['date'].max()}",
            'Most Active User': df['user_id'].mode().iloc[0] if not df.empty else 'N/A',
            'Average Daily Attendance': round(len(df) / df['date'].nunique(), 2) if not df.empty else 0
        }
        return pd.DataFrame(list(stats.items()), columns=['Statistic', 'Value'])

    def _generate_daily_summary(self, df):
        """Generate daily attendance summary"""
        if df.empty:
            return pd.DataFrame()
            
        daily_summary = df.groupby('date').agg({
            'user_id': 'count',
            'name': 'nunique'
        }).rename(columns={
            'user_id': 'Total Attendance',
            'name': 'Unique Users'
        })
        return daily_summary

    def _add_visualizations(self, pdf, df):
        """Add visualizations to PDF report"""
        if df.empty:
            return
            
        # Create temporary directory for plots
        temp_dir = os.path.join(self.reports_dir, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Daily attendance trend
            plt.figure(figsize=(10, 6))
            daily_counts = df.groupby('date')['user_id'].count()
            sns.lineplot(data=daily_counts)
            plt.title('Daily Attendance Trend')
            plt.xticks(rotation=45)
            plt.tight_layout()
            trend_plot = os.path.join(temp_dir, 'trend.png')
            plt.savefig(trend_plot)
            plt.close()
            
            # User distribution
            plt.figure(figsize=(10, 6))
            user_counts = df['name'].value_counts()
            sns.barplot(x=user_counts.values, y=user_counts.index)
            plt.title('Attendance by User')
            plt.tight_layout()
            user_plot = os.path.join(temp_dir, 'users.png')
            plt.savefig(user_plot)
            plt.close()
            
            # Add plots to PDF
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Visualizations', 0, 1, 'L')
            
            pdf.image(trend_plot, x=10, y=30, w=190)
            pdf.image(user_plot, x=10, y=160, w=190)
            
            # Cleanup temporary files
            os.remove(trend_plot)
            os.remove(user_plot)
            os.rmdir(temp_dir)
            
        except Exception as e:
            print(f"❌ Error generating visualizations: {str(e)}")

    def _generate_filename(self, extension, start_date=None, end_date=None, user_id=None):
        """Generate filename for report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if user_id:
            return f"attendance_report_{user_id}_{timestamp}.{extension}"
        elif start_date and end_date:
            return f"attendance_report_{start_date}_to_{end_date}_{timestamp}.{extension}"
        else:
            return f"attendance_report_all_{timestamp}.{extension}"
