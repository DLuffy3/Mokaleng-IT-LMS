import json

from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from learning_management_app.models import Subjects, CourseSession, Students, Attendance, AttendanceReport, Staff, \
    LeaveReportStaff, StaffFeedback, UserType, Courses, StaffNotification, StudentResult


def staff_home(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    course_id_list = []
    for subject in subjects:
        course = Courses.objects.get(id=subject.course_id.id)
        course_id_list.append(course.id)

    final_course = []
    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)

    students_count = Students.objects.filter(course_id__in=final_course).count()
    attendance_count = Attendance.objects.filter(subject_id__in=subjects).count()
    subjects_count = subjects.count()

    subject_list = []
    subject_attendance_list = []
    for subject in subjects:
        subject_attendance_count = Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        subject_attendance_list.append(subject_attendance_count)

    student_attendance = Students.objects.filter(course_id__in=final_course)
    student_list = []
    student_absent_list = []
    student_present_list = []
    for student in student_attendance:
        attendance_present_count = AttendanceReport.objects.filter(status=True,
                                                                   student_id=student.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(status=False,
                                                                  student_id=student.id).count()
        student_list.append(student.user_type.username)
        student_present_list.append(attendance_present_count)
        student_absent_list.append(attendance_absent_count)

    return render(request, "staff_components/staff_home_component.html", {"students_count": students_count,
                                                                          "attendance_count": attendance_count,
                                                                          "subjects_count": subjects_count,
                                                                          "subject_list": subject_list,
                                                                          "subject_attendance_list": subject_attendance_list,
                                                                          "student_list": student_list,
                                                                          "student_present_list": student_present_list,
                                                                          "student_absent_list": student_absent_list})


def staff_take_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    course_sessions = CourseSession.objects.all()
    return render(request, "staff_components/staff_take_attendance.html",
                  {"subjects": subjects,
                   "course_sessions": course_sessions})


@csrf_exempt
def get_students(request):
    try:
        subject_id = request.POST.get("subject")
        course_session_dates = request.POST.get("course_session")

        subject = Subjects.objects.get(id=subject_id)
        course_session = CourseSession.objects.get(id=course_session_dates)
        students = Students.objects.filter(course_id=subject.course_id,
                                           course_session_id=course_session)
        list_data = []
        for student in students:
            data_small = {"id": student.user_type.id,
                          "name": student.user_type.first_name + " " + student.user_type.last_name}
            list_data.append(data_small)
        return JsonResponse(json.dumps(list_data),
                            content_type="application/json",
                            safe=False)
    except Exception as e:
        print(e)


@csrf_exempt
def save_attendance_data(request):
    try:
        student_ids = request.POST.get("student_ids")
        attendance_date = request.POST.get("attendance_date")
        subject_id = request.POST.get("subject_id")
        course_session_id = request.POST.get("course_session_id")
        data = json.loads(student_ids)
        subject_model = Subjects.objects.get(id=subject_id)
        course_session = CourseSession.objects.get(id=course_session_id)
        attendance = Attendance(subject_id=subject_model,
                                attendance_date=attendance_date,
                                course_session_id=course_session)
        attendance.save()
        for student_id in data:
            student = Students.objects.get(user_type=student_id['id'])
            attendance_report = AttendanceReport(student_id=student,
                                                 attendance_id=attendance,
                                                 status=student_id['status'])
            attendance_report.save()
        return HttpResponse("Ok")
    except Exception as e:
        print(e)
        return HttpResponse("Error")


def staff_update_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    course_sessions = CourseSession.objects.all()
    return render(request, "staff_components/staff_update_attendance.html", {"subjects": subjects,
                                                                             "course_sessions": course_sessions})


@csrf_exempt
def get_attendance_dates(request):
    try:
        subject_id = request.POST.get("subject_id")
        course_session_id = request.POST.get("course_session_id")
        subject_data = Subjects.objects.get(id=subject_id)
        course_data = CourseSession.objects.get(id=course_session_id)
        attendance = Attendance.objects.filter(subject_id=subject_data,
                                               course_session_id=course_data)
        attendance_data = []
        for attendance_single in attendance:
            data = {"id": attendance_single.id,
                    "attendance_date": str(attendance_single.attendance_date),
                    "course_session_id": attendance_single.course_session_id.id}
            attendance_data.append(data)

        return JsonResponse(json.dumps(attendance_data),
                            safe=False)
    except Exception as e:
        print(e)


@csrf_exempt
def get_attendance_student(request):
    try:
        attendance_date = request.POST.get("attendance_date")
        attendance = Attendance.objects.get(id=attendance_date)
        attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
        list_data = []
        for student in attendance_data:
            data_small = {"id": student.student_id.user_type.id,
                          "name": student.student_id.user_type.first_name + " " + student.student_id.user_type.last_name,
                          "status": student.status}
            list_data.append(data_small)
        return JsonResponse(json.dumps(list_data),
                            content_type="application/json",
                            safe=False)
    except Exception as e:
        print(e)


@csrf_exempt
def update_attendance_data(request):
    try:
        student_ids = request.POST.get("student_ids")
        attendance_date = request.POST.get("attendance_date")
        attendance = Attendance.objects.get(id=attendance_date)
        data = json.loads(student_ids)
        for student_id in data:
            student = Students.objects.get(user_type=student_id['id'])
            attendance_report = AttendanceReport.objects.get(student_id=student,
                                                             attendance_id=attendance)
            attendance_report.status = student_id['status']
            attendance_report.save()
        return HttpResponse("Ok")
    except Exception as e:
        print(e)
        return HttpResponse("Error")


def staff_apply_leave(request):
    staff_data = Staff.objects.get(user_type=request.user.id)
    leave_data = LeaveReportStaff.objects.filter(staff_id=staff_data)
    return render(request, "staff_components/staff_apply_leave.html",
                  {"leave_data": leave_data})


def save_staff_apply_leave(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("staff_apply_leave"))
    else:
        leave_date = request.POST.get("leave_date")
        leave_reason = request.POST.get("leave_reason")
        try:
            staff_data = Staff.objects.get(user_type=request.user.id)
            leave_report = LeaveReportStaff(staff_id=staff_data,
                                            leave_date=leave_date,
                                            leave_message=leave_reason,
                                            leave_status=0)
            leave_report.save()
            messages.success(request, "Leave Application has been Successfully sent")
            return HttpResponseRedirect("staff_apply_leave")
        except Exception as e:
            print(e)  # Print the exception for debugging
            messages.error(request, "Failed to send Leave Application")
            return HttpResponseRedirect("staff_apply_leave")


def staff_feedback(request):
    staff_id = Staff.objects.get(user_type=request.user.id)
    feedback_data = StaffFeedback.objects.filter(staff_id=staff_id)
    return render(request, "staff_components/staff_feedback.html",
                  {"feedback_data": feedback_data})


def save_staff_feedback(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("staff_feedback"))
    else:
        feedback_message = request.POST.get("feedback_message")
        try:
            staff_data = Staff.objects.get(user_type=request.user.id)
            staff_feedback_data = StaffFeedback(staff_id=staff_data,
                                                feedback=feedback_message,
                                                feedback_message="")
            staff_feedback_data.save()
            messages.success(request, "Feedback has been Successfully sent")
            return HttpResponseRedirect("staff_feedback")
        except Exception as e:
            print(e)  # Print the exception for debugging
            messages.error(request, "Failed to send Feedback")
            return HttpResponseRedirect("staff_feedback")


def staff_profile(request):
    user = UserType.objects.get(id=request.user.id)
    return render(request, "staff_components/staff_profile_component.html",
                  {"user": user})


def edit_staff_profile(request):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse("staff_profile"))
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        try:
            user_type = UserType.objects.get(id=request.user.id)
            user_type.first_name = first_name
            user_type.last_name = last_name
            if password is not None and password != "":
                user_type.set_password(password)
            user_type.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("staff_profile"))
        except Exception as e:
            print(e)
            messages.error(request, "Failed to Updated Profile")
            return HttpResponseRedirect(reverse("staff_profile"))


@csrf_exempt
def staff_fcmtoken_save(request):
    token = request.POST.get('token')
    try:
        staff = Staff.objects.get(user_type=request.user.id)
        staff.fcm_token = token
        staff.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")


def staff_all_notification(request):
    staff = Staff.objects.get(user_type=request.user.id)
    notifications = StaffNotification.objects.filter(staff_id=staff.id)
    return render(request, "staff_components/all_staff_notification.html", {"notifications": notifications})


def staff_add_result(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    course_sessions = CourseSession.objects.all()
    return render(request, "staff_components/staff_add_result.html", {"subjects": subjects,
                                                                      "course_sessions": course_sessions})


def save_student_result(request):
    if request.method != 'POST':
        return HttpResponseRedirect('staff_add_result')
    student_admin_id = request.POST.get('student_list')
    assignment_marks = request.POST.get('assignment_marks')
    exam_marks = request.POST.get('exam_marks')
    subject_id = request.POST.get('subject')

    student_obj = Students.objects.get(user_type=student_admin_id)
    subject_obj = Subjects.objects.get(id=subject_id)

    try:
        check_exist = StudentResult.objects.filter(subject_id=subject_obj, student_id=student_obj).exists()
        if check_exist:
            result = StudentResult.objects.get(subject_id=subject_obj, student_id=student_obj)
            result.subject_assignment_marks = assignment_marks
            result.subject_exam_marks = exam_marks
            result.save()
            messages.success(request, "Successfully Updated Result")
            return HttpResponseRedirect(reverse("staff_add_result"))
        else:
            result = StudentResult(student_id=student_obj, subject_id=subject_obj, subject_exam_marks=exam_marks,
                                   subject_assignment_marks=assignment_marks)
            result.save()
            messages.success(request, "Successfully Added Result")
            return HttpResponseRedirect(reverse("staff_add_result"))
    except:
        messages.error(request, "Failed to Add Result")
        return HttpResponseRedirect(reverse("staff_add_result"))


@csrf_exempt
def fetch_result_student(request):
    subject_id = request.POST.get('subject_id')
    student_id = request.POST.get('student_id')
    student_obj = Students.objects.get(user_type=student_id)
    result = StudentResult.objects.filter(student_id=student_obj.id, subject_id=subject_id).exists()
    if result:
        result = StudentResult.objects.get(student_id=student_obj.id, subject_id=subject_id)
        result_data = {"exam_marks": result.subject_exam_marks, "assign_marks": result.subject_assignment_marks}
        return HttpResponse(json.dumps(result_data))
    else:
        return HttpResponse("False")
