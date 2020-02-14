from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .authentication import JWTAuthentication
from django.contrib.auth import get_user_model
import pandas as pd
from .models import *
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class CoursesNotEnrolledTillNow(APIView):
    authentication_classes = (JWTAuthentication, )

    def get(self, request):
        # Url: /api/courses_not_enrolled/
        # RequestBody: None
        user_id = request.user.get('user_id')
        user = User.objects.get(id=user_id)
        all_avl_course = CourseProvidedByTeacher.objects.all()
        course_teacher_df = pd.DataFrame(list(all_avl_course.values()))
        courses = Course.objects.all()
        course_df = pd.DataFrame(list(courses.values()))
        teachers = User.objects.filter(user_type=2)
        teacher_df = pd.DataFrame(list(teachers.values()))
        teacher_df = teacher_df[["id", "full_name"]]
        teacher_df = teacher_df.rename(columns={"id": "teacher_id", "full_name": "teacher_name"})
        ndf = course_teacher_df.merge(teacher_df, left_on="teacher_id", right_on="teacher_id", how="inner")
        ndf = ndf.merge(course_df, left_on="course_id", right_on="course_id", how="inner")
        enrolled_courses = StudentEnrolledToCourse.objects.filter(student=user, is_active=True)
        if len(enrolled_courses) > 0:
            enrolled_courses_df = pd.DataFrame(list(enrolled_courses.values()))
            course_teacher_list = enrolled_courses_df["course_teacher_id"].tolist()
            tempdf = course_teacher_df[course_teacher_df["course_teacher_id"].isin(course_teacher_list)]
            all_teacher_list = ndf["teacher_id"].tolist()
            en_teacher_list = tempdf["teacher_id"].tolist()
            all_teacher_list = filter(lambda x: x not in  en_teacher_list, all_teacher_list)
            ndf = ndf[ndf["teacher_id"].isin(all_teacher_list)]
        return Response(ndf.to_dict("records"), status=status.HTTP_200_OK)


class EnrollCourse(APIView):
    authentication_classes = (JWTAuthentication, )

    def get(self, request):
        # Url: /api/courses_not_enrolled/
        # RequestBody: None
        user_id = request.user.get('user_id')
        user = User.objects.get(id=user_id)
        enrolled_courses = StudentEnrolledToCourse.objects.filter(student=user, is_active=True)
        if len(enrolled_courses) == 0:
            return Response({"Info": "You haven't enrolled for any courses till now"},status=status.HTTP_204_NO_CONTENT)
        enrolled_courses_df = pd.DataFrame(list(enrolled_courses.values()))
        course_teacher = CourseProvidedByTeacher.objects.filter(
            course_teacher_id__in=enrolled_courses_df["course_teacher_id"].tolist()
            )
        course_teacher_df = pd.DataFrame(list(course_teacher.values()))
        courses = Course.objects.filter(course_id__in=course_teacher_df["course_id"].tolist())
        course_df = pd.DataFrame(list(courses.values()))
        teachers = User.objects.filter(id__in=course_teacher_df["teacher_id"].tolist())
        teacher_df = pd.DataFrame(list(teachers.values()))
        teacher_df = teacher_df[["id", "full_name"]]
        teacher_df = teacher_df.rename(columns={"id": "teacher_id", "full_name": "teacher_name"})
        ndf = course_teacher_df.merge(teacher_df, left_on="teacher_id", right_on="teacher_id", how="inner")
        ndf = ndf.merge(course_df, left_on="course_id", right_on="course_id", how="inner")
        #ndf =  course_teacher_df.merge(ndf, left_on="course_teacher_id", right_on="course_teacher_id", how="inner")
        return Response(ndf.to_dict("records"), status=status.HTTP_200_OK)

    def post(self, request):
        # Url: /api/courses_not_enrolled/
        # RequestBody: { courses: [course_teacher_id1, course_teacher_id2,....]}
        data = request.data
        user_id = request.user.get('user_id')
        user = User.objects.get(id=user_id)
        if "courses" not in data.keys():
            return Response({"Error": "Please Provide list of course ids to enroll with"},status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            for course_teacher_id in data["courses"]:
                course_teacher = CourseProvidedByTeacher.objects.get(course_teacher_id=course_teacher_id)
                try:
                    StudentEnrolledToCourse.objects.get(student=user, course_teacher=course_teacher, is_active=True)
                except ObjectDoesNotExist:
                    StudentEnrolledToCourse.objects.create(student=user, course_teacher=course_teacher)
        return Response({"Success": "course enrollment successfull"}, status=status.HTTP_200_OK)

    def patch(self, request):
        # Url: /api/courses_not_enrolled/
        # RequestBody: { course_teacher_id: course_teacher_id}
        # As of now PATCH means dlist  the enrollment
        data = request.data
        user_id = request.user.get('user_id')
        user = User.objects.get(id=user_id)
        if "course_teacher_id" not in data.keys():
            return Response({"Error": "Please Provide the course_teacher_id to delist"}, status=status.HTTP_400_BAD_REQUEST)
        course_teacher_id = data["course_teacher_id"]
        course_teacher = CourseProvidedByTeacher.objects.get(course_teacher_id=course_teacher_id)
        try:
            course_obj = StudentEnrolledToCourse.objects.get(
                student=user,
                course_teacher=course_teacher, is_active=True)
        except ObjectDoesNotExist:
            pass
        course_obj.is_active = False
        course_obj.feedback = data["remarks"]
        course_obj.save()
        return Response({"Success": "course dlisting successfull"}, status=status.HTTP_200_OK)