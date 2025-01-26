import datetime

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from learning_management_app.models import Subjects, Students, Courses, UserType, Attendance, AttendanceReport, \
    LeaveReportStudent, StudentFeedback, StudentNotification, StudentResult


def student_home(request):
    student_data = Students.objects.get(user_type=request.user.id)
    attendance_total = AttendanceReport.objects.filter(student_id=student_data).count()
    attendance_present = AttendanceReport.objects.filter(student_id=student_data,
                                                         status=True).count()
    attendance_absent = AttendanceReport.objects.filter(student_id=student_data,
                                                        status=False).count()
    course = Courses.objects.get(id=student_data.course_id.id)
    subjects = Subjects.objects.filter(course_id=course).count()
    subject_name = []
    data_present = []
    data_absent = []
    subject_data = Subjects.objects.filter(course_id=student_data.course_id)
    for subject in subject_data:
        attendance = Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count = AttendanceReport.objects.filter(attendance_id__in=attendance,
                                                                   student_id=student_data.id,
                                                                   status=True).count()
        attendance_absent_count = AttendanceReport.objects.filter(attendance_id__in=attendance,
                                                                  student_id=student_data.id,
                                                                  status=False).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)
    return render(request, "student_components/student_home_component.html",
                  {"total_attendance": attendance_total,
                   "present_attendance": attendance_present,
                   "absent_attendance": attendance_absent,
                   "subjects": subjects,
                   "subject_name": subject_name,
                   "present_data": data_present,
                   "absent_data": data_absent,
                   "student_data": student_data})


def student_view_attendance(request):
    try:
        student_data = Students.objects.get(user_type=request.user.id)
        course = student_data.course_id
        subjects = Subjects.objects.filter(course_id=course.id)
        return render(request, "student_components/student_view_attendance.html",
                      {"subjects": subjects,
                       "student_data": student_data})
    except Exception as e:
        print(e)


def student_attendance_data(request):
    try:
        subject_id = request.POST.get('subject')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        start_data = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_data = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        subject_data = Subjects.objects.get(id=subject_id)
        user_id = UserType.objects.get(id=request.user.id)
        student_data = Students.objects.get(user_type=user_id)

        attendance = Attendance.objects.filter(attendance_date__range=(start_data, end_data),
                                               subject_id=subject_data)
        attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendance,
                                                             student_id=student_data)

        return render(request, "student_components/student_attendance_data.html",
                      {"attendance_reports": attendance_reports,
                       "student_data": student_data})
    except Exception as e:
        print(e)


def student_apply_leave(request):
    student_data = Students.objects.get(user_type=request.user.id)
    leave_data = LeaveReportStudent.objects.filter(student_id=student_data)
    return render(request, "student_components/student_apply_leave.html",
                  {"leave_data": leave_data})


def save_student_apply_leave(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("student_apply_leave"))
    else:
        leave_date = request.POST.get("leave_date")
        leave_reason = request.POST.get("leave_reason")
        try:
            staff_data = Students.objects.get(user_type=request.user.id)
            leave_report = LeaveReportStudent(student_id=staff_data,
                                              leave_date=leave_date,
                                              leave_message=leave_reason,
                                              leave_status=0)
            leave_report.save()
            messages.success(request, "Leave Application has been Successfully sent")
            return HttpResponseRedirect("student_apply_leave")
        except Exception as e:
            print(e)  # Print the exception for debugging
            messages.error(request, "Failed to send Leave Application")
            return HttpResponseRedirect("student_apply_leave")


def student_feedback(request):
    student_data = Students.objects.get(user_type=request.user.id)
    feedback_data = StudentFeedback.objects.filter(student_id=student_data)
    return render(request, "student_components/student_feedback.html",
                  {"feedback_data": feedback_data,
                   "student_data": student_data})


def save_student_feedback(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("student_feedback"))
    else:
        feedback_message = request.POST.get("feedback_message")
        try:
            student_data = Students.objects.get(user_type=request.user.id)
            student_feedback_data = StudentFeedback(student_id=student_data,
                                                    feedback=feedback_message,
                                                    feedback_message="")
            student_feedback_data.save()
            messages.success(request, "Feedback has been Successfully sent")
            return HttpResponseRedirect("student_feedback")
        except Exception as e:
            print(e)  # Print the exception for debugging
            messages.error(request, "Failed to send Feedback")
            return HttpResponseRedirect("student_feedback")


def student_profile(request):
    user = UserType.objects.get(id=request.user.id)
    return render(request, "student_components/student_profile_component.html",
                  {"user": user})


def edit_student_profile(request):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse("student_profile"))
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
            return HttpResponseRedirect(reverse("student_profile"))
        except Exception as e:
            print(e)
            messages.error(request, "Failed to Updated Profile")
            return HttpResponseRedirect(reverse("student_profile"))


@csrf_exempt
def student_fcmtoken_save(request):
    token = request.POST.get('token')
    try:
        student = Students.objects.get(user_type=request.user.id)
        student.fcm_token = token
        student.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")


def student_all_notification(request):
    student = Students.objects.get(user_type=request.user.id)
    notifications = StudentNotification.objects.filter(student_id=student.id)
    student_data = Students.objects.get(user_type=request.user.id)
    return render(request, "student_components/all_student_notification.html", {"notifications": notifications,
                                                                                "student_data": student_data})


def student_view_result(request):
    student_data = Students.objects.get(user_type=request.user.id)
    student_results = StudentResult.objects.filter(student_id=student_data.id)
    return render(request, "student_components/student_results.html", {"student_results": student_results,
                                                                                "student_data": student_data})
