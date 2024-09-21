import openpyxl

def check_enrollment_exists_TE(enrollment_number, filename='TE.xlsx'):

    wb = openpyxl.load_workbook(filename='workbooks/TE.xlsx',data_only=True)
    ws = wb['Attendance'] 

    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[1] == enrollment_number: 
            return True  # Enrollment number found

    return False  # Enrollment number not found
# Example usage

if check_enrollment_exists_TE('R-22-0124'):
    print("yes")
