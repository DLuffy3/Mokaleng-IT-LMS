import json

import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from learning_management_app.forms import EditStudentForm, AddStudentForm
from learning_management_app.models import UserType, Courses, Subjects, Staff, Students, CourseSession, StudentFeedback, \
    StaffFeedback, LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport, StudentNotification, \
    StaffNotification


def admin_home(request):
    student_count = Students.objects.all().count()
    staff_count = Staff.objects.all().count()
    subject_count = Subjects.objects.all().count()
    course_count = Courses.objects.all().count()

    course_all = Courses.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []
    for course in course_all:
        subjects = Subjects.objects.filter(course_id=course.id).count()
        students = Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)

    return render(request, "sysadmin_components/admin_home_component.html", {"student_count": student_count,
                                                                             "staff_count": staff_count,
                                                                             "subject_count": subject_count,
                                                                             "course_count": course_count,
                                                                             "course_name_list": course_name_list,
                                                                             "subject_count_list": subject_count_list,
                                                                             "student_count_list_in_course": student_count_list_in_course})


def add_staff(request):
    return render(request, "sysadmin_components/add_staff_component.html")


def add_staff_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        address = request.POST.get("address")
        try:
            user = UserType.objects.create_user(username=username,
                                                password=password,
                                                email=email,
                                                last_name=last_name,
                                                first_name=first_name,
                                                user_type=2)
            user.staff.address = address
            user.save()
            messages.success(request, "Successfully Added Staff")
            return HttpResponseRedirect("/add_staff")
        except Exception as e:
            print(e)  # Print the exception for debugging
            messages.error(request, "Failed To Add Staff")
            return HttpResponseRedirect("/add_staff")


def add_student(request):
    courses = Courses.objects.all()
    form = AddStudentForm()
    return render(request, "sysadmin_components/add_student_component.html", {"courses": courses, "form": form})


def add_student_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        form = AddStudentForm(request.POST, request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            address = form.cleaned_data["address"]
            course_session_id = form.cleaned_data["session"]
            course_id = form.cleaned_data["course"]
            gender = form.cleaned_data["gender"]

            profile_pic = request.FILES.get("profile_pic")
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            profile_pic_url = fs.url(filename)

            try:
                user = UserType.objects.create_user(username=username,
                                                    password=password,
                                                    email=email,
                                                    last_name=last_name,
                                                    first_name=first_name,
                                                    user_type=3)
                user.students.address = address
                course_obj = Courses.objects.get(id=course_id)
                user.students.course_id = course_obj
                course_session = CourseSession.objects.get(id=course_session_id)
                user.students.course_session_id = course_session
                user.students.gender = gender
                user.students.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Successfully Added Student")
                return HttpResponseRedirect(reverse("add_student"))
            except Exception as e:
                print(e)
                messages.error(request, "Failed to Add Student")
                return HttpResponseRedirect(reverse("add_student"))
        else:
            form = AddStudentForm(request.POST)
            return render(request, "sysadmin_components/add_student_component.html", {"form": form})


def add_course(request):
    return render(request, "sysadmin_components/add_course_component.html")


def add_course_save(request):
    if request.method != "POST":
        return HttpResponse("Method Not Allowed")
    else:
        course_name = request.POST.get("course_name")
        try:
            course = Courses(course_name=course_name)
            course.save()
            messages.success(request, "Successfully Added A New Course")
            return HttpResponseRedirect("/add_course")
        except Exception as e:
            print(e)  # Print the exception for debugging
            messages.error(request, "Failed To Add New Course")
            return HttpResponseRedirect("/add_course")


def add_subject(request):
    courses = Courses.objects.all()
    staffs = UserType.objects.filter(user_type=2)
    return render(request, "sysadmin_components/add_subject_component.html", {"staffs": staffs, "courses": courses})


def add_subject_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_name = request.POST.get("subject_name")
        course_id = request.POST.get("course")
        course = Courses.objects.get(id=course_id)
        staff_id = request.POST.get("staff")
        staff = UserType.objects.get(id=staff_id)
        try:
            subject = Subjects(subject_name=subject_name,
                               course_id=course,
                               staff_id=staff)
            subject.save()
            messages.success(request, "Successfully Added Subject")
            return HttpResponseRedirect("add_subject")
        except Exception as e:
            print(e)  # Print the exception for debugging
            messages.error(request, "Failed to Add Subject")
            return HttpResponseRedirect("add_subject")


def manage_staff(request):
    staff = Staff.objects.all()
    return render(request, "sysadmin_components/manage_staff_component.html", {"staffs": staff})


def manage_student(request):
    students = Students.objects.all()
    return render(request, "sysadmin_components/manage_student_component.html", {"students": students})


def manage_course(request):
    courses = Courses.objects.all()
    return render(request, "sysadmin_components/manage_course_component.html", {"courses": courses})


def manage_subject(request):
    subjects = Subjects.objects.all()
    return render(request, "sysadmin_components/manage_subject_component.html", {"subjects": subjects})


def manage_course_sessions(request):
    return render(request, "sysadmin_components/manage_course_sessions_component.html")


def add_course_session_save(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("manage_course_sessions"))
    else:
        course_start_date = request.POST.get("course_start_date")
        course_end_date = request.POST.get("course_end_date")

        try:
            course_session = CourseSession(session_start_year=course_start_date,
                                           session_end_year=course_end_date)
            course_session.save()
            messages.success(request, "Successfully Added Course Session")
            return HttpResponseRedirect(reverse("manage_course_sessions"))
        except Exception as e:
            print(e)  # Print the exception for debugging
            messages.error(request, "Failed to Add Course Session")
            return HttpResponseRedirect(reverse("manage_course_sessions"))


def edit_staff(request, staff_id):
    staff = Staff.objects.get(user_type=staff_id)
    return render(request, "sysadmin_components/edit_staff_component.html", {"staff": staff, "id": staff_id})


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get("staff_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        address = request.POST.get("address")

        try:
            user = UserType.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            staff_model = Staff.objects.get(user_type=staff_id)
            staff_model.address = address
            staff_model.save()
            messages.success(request, "Successfully Edited Staff")
            return HttpResponseRedirect(reverse("edit_staff", kwargs={"staff_id": staff_id}))
        except Exception as e:
            print(e)  # Print the exception for debugging
            messages.error(request, "Failed to Edit Staff")
            return HttpResponseRedirect(reverse("edit_staff", kwargs={"staff_id": staff_id}))


def edit_student(request, student_id):
    request.session['student_id'] = student_id
    student = Students.objects.get(user_type=student_id)
    form = EditStudentForm()
    form.fields['email'].initial = student.user_type.email
    form.fields['first_name'].initial = student.user_type.first_name
    form.fields['last_name'].initial = student.user_type.last_name
    form.fields['username'].initial = student.user_type.username
    form.fields['address'].initial = student.address
    form.fields['course'].initial = student.course_id.id
    form.fields['gender'].initial = student.gender
    form.fields['course_session_id'].initial = student.course_session_id.id
    return render(request, "sysadmin_components/edit_student_component.html",
                  {"form": form, "student_id": student_id, "username": student.user_type.username})


def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        student_id = request.session.get("student_id")
        if student_id is None:
            return HttpResponseRedirect(reverse("manage_student"))

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            address = form.cleaned_data["address"]
            course_session_id = form.cleaned_data["course_session_id"]
            course_id = form.cleaned_data["course"]
            gender = form.cleaned_data["gender"]

            if request.FILES.get('profile_pic', False):
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                user = UserType.objects.get(id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.username = username
                user.email = email
                user.save()

                student = Students.objects.get(user_type=student_id)
                student.address = address
                course_session = CourseSession.objects.get(id=course_session_id)
                student.course_session_id = course_session
                student.gender = gender
                course = Courses.objects.get(id=course_id)
                student.course_id = course
                if profile_pic_url is not None:
                    student.profile_pic = profile_pic_url
                student.save()
                del request.session['student_id']
                messages.success(request, "Successfully Edited Student")
                return HttpResponseRedirect(reverse("edit_student", kwargs={"student_id": student_id}))
            except Exception as e:
                print(e)
                messages.error(request, "Failed to Edit Student")
                return HttpResponseRedirect(reverse("edit_student", kwargs={"student_id": student_id}))
        else:
            form = EditStudentForm(request.POST)
            student = Students.objects.get(user_type=student_id)
            return render(request, "sysadmin_components/edit_student_component.html",
                          {"form": form, "id": student_id, "username": student.user_type.username})


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    staffs = UserType.objects.filter(user_type=2)
    return render(request, "sysadmin_components/edit_subject_component.html",
                  {"subject": subject, "staffs": staffs, "courses": courses, "id": subject_id})


def edit_subject_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        subject_id = request.POST.get("subject_id")
        subject_name = request.POST.get("subject_name")
        staff_id = request.POST.get("staff")
        course_id = request.POST.get("course")

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name
            staff = UserType.objects.get(id=staff_id)
            subject.staff_id = staff
            course = Courses.objects.get(id=course_id)
            subject.course_id = course
            subject.save()

            messages.success(request, "Successfully Edited Subject")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id": subject_id}))
        except Exception as e:
            print(e)
            messages.error(request, "Failed to Edit Subject")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id": subject_id}))


def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    return render(request, "sysadmin_components/edit_course_component.html", {"course": course, "id": course_id})


def edit_course_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        course_id = request.POST.get("course_id")
        course_name = request.POST.get("course")

        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()
            messages.success(request, "Successfully Edited Course")
            return HttpResponseRedirect(reverse("edit_course", kwargs={"course_id": course_id}))
        except Exception as e:
            print(e)
            messages.error(request, "Failed to Edit Course")
            return HttpResponseRedirect(reverse("edit_course", kwargs={"course_id": course_id}))


@csrf_exempt
def check_email_exist(request):
    try:
        email = request.POST.get("email")
        user_data = UserType.objects.filter(email=email).exists()
        if user_data:
            return HttpResponse(True)
        else:
            return HttpResponse(False)
    except Exception as e:
        print(e)


@csrf_exempt
def check_username_exist(request):
    try:
        username = request.POST.get("username")
        user_data = UserType.objects.filter(username=username).exists()
        if user_data:
            return HttpResponse(True)
        else:
            return HttpResponse(False)
    except Exception as e:
        print(e)


def staff_feedback_data(request):
    staff_feedback = StaffFeedback.objects.all()
    return render(request, "sysadmin_components/staff_feedback_component.html",
                  {"staff_feedback": staff_feedback})


@csrf_exempt
def save_staff_feedback_reply(request):
    feedback_id = request.POST.get("id")
    feedback_message = request.POST.get("message")

    try:
        feedback = StaffFeedback.objects.get(id=feedback_id)
        feedback.feedback_message = feedback_message
        feedback.save()
        return HttpResponse("True")
    except Exception as e:
        print(e)
        return HttpResponse("False")


def student_feedback_data(request):
    student_feedback = StudentFeedback.objects.all()
    return render(request, "sysadmin_components/student_feedback_component.html",
                  {"student_feedback": student_feedback})


@csrf_exempt
def save_student_feedback_reply(request):
    feedback_id = request.POST.get("id")
    feedback_message = request.POST.get("message")

    try:
        feedback = StudentFeedback.objects.get(id=feedback_id)
        feedback.feedback_message = feedback_message
        feedback.save()
        return HttpResponse("True")
    except Exception as e:
        print(e)
        return HttpResponse("False")


def staff_leave_view(request):
    applied_leave = LeaveReportStaff.objects.all()
    return render(request, "sysadmin_components/staff_leave_view.html",
                  {"applied_leave": applied_leave})


def staff_approve_leave(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))


def staff_disapprove_leave(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return HttpResponseRedirect(reverse("staff_leave_view"))


def student_leave_view(request):
    applied_leave = LeaveReportStudent.objects.all()
    return render(request, "sysadmin_components/student_leave_view.html",
                  {"applied_leave": applied_leave})


def student_approve_leave(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))


def student_disapprove_leave(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))


def view_attendance_report(request):
    subjects = Subjects.objects.all()
    course_sessions = CourseSession.objects.all()
    return render(request, "sysadmin_components/view_attendance_report.html", {"subjects": subjects,
                                                                               "course_sessions": course_sessions})


@csrf_exempt
def admin_get_attendance_dates(request):
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
def admin_get_attendance_student(request):
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
def admin_update_attendance_data(request):
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


def admin_profile(request):
    user = UserType.objects.get(id=request.user.id)
    return render(request, "sysadmin_components/admin_profile_component.html",
                  {"user": user})


def edit_admin_profile(request):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse("admin_profile"))
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
            return HttpResponseRedirect(reverse("admin_profile"))
        except Exception as e:
            print(e)
            messages.error(request, "Failed to Updated Profile")
            return HttpResponseRedirect(reverse("admin_profile"))

def admin_send_notification_student(request):
    students = Students.objects.all()
    return render(request,"sysadmin_components/student_notification.html",{"students": students})

def admin_send_notification_staff(request):
    staffs = Staff.objects.all()
    return render(request,"sysadmin_components/staff_notification.html",{"staffs": staffs})

@csrf_exempt
def send_student_notification(request):
    id = request.POST.get("id")
    message = request.POST.get("message")
    student = Students.objects.get(user_type=id)
    token = student.fcm_token
    url = "https://fcm.googleapis.com/fcm/send"
    body = {
        "notification":{
            "title":"Mokaleng IT LMS",
            "body":message,
            "click_action": "https://mokaleng-it-lms-b1d8ac2b8b98.herokuapp.com/student_all_notification",
            "icon": "https://mokaleng-it-lms-b1d8ac2b8b98.herokuapp.com/static/dist/img/user2-160x160.jpg"
        },
        "to":token
    }
    headers = {"Content-Type":"application/json","Authorization":"key=SERVER_KEY_HERE"}
    data = requests.post(url,data=json.dumps(body),headers=headers)
    notification = StudentNotification(student_id=student,message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")

@csrf_exempt
def send_staff_notification(request):
    id = request.POST.get("id")
    message = request.POST.get("message")
    staff = Staff.objects.get(user_type=id)
    token = staff.fcm_token
    url = "https://fcm.googleapis.com/fcm/send"
    body = {
        "notification":{
            "title":"Mokaleng IT LMS",
            "body":message,
            "click_action":"https://mokaleng-it-lms-b1d8ac2b8b98.herokuapp.com/staff_all_notification",
            "icon":"https://mokaleng-it-lms-b1d8ac2b8b98.herokuapp.com/static/dist/img/user2-160x160.jpg"
        },
        "to":token
    }
    headers = {"Content-Type":"application/json","Authorization": "key=BHmTGHrxW2nM52X_Bgxahz42vBvttsvoqGY7cQsbIddAM5FEJgdIrmRwRcewQr_MuF6o3nhur1q8Y-IiHx5KuEE"}
    data = requests.post(url,data=json.dumps(body),headers=headers)
    notification = StaffNotification(staff_id=staff,message=message)
    notification.save()
    print(data.text)
    return HttpResponse("True")

def student_all_notification(request):
    student=Students.objects.get(admin=request.user.id)
    notifications=StudentNotification.objects.filter(student_id=student.id)
    return render(request,"student_template/all_notification.html",{"notifications":notifications})

def student_view_result(request):
    pass
    #student=Students.objects.get(admin=request.user.id)
    #studentresult=StudentResult.objects.filter(student_id=student.id)
    #return render(request,"student_template/student_result.html",{"studentresult":studentresult})