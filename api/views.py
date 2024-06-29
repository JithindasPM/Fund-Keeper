from django.shortcuts import render
from rest_framework.viewsets import ViewSet,ModelViewSet
from django.contrib.auth.models import User
from api.serializers import *
from api.models import *
from api.permissions import *
from rest_framework import status,authentication,permissions
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from django.db.models import Sum
from datetime import datetime


# Create your views here.

class SignUp_View(ViewSet):
    def create(self,request,*args,**kwargs):
        serializer=UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
class ExpenseViewSet(ModelViewSet):

    queryset=Expense.objects.all()
    serializer_class=ExpenseSerializer
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[OwnerOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def list(self, request, *args, **kwargs):
        

        qs=Expense.objects.filter(owner=request.user)

        if 'month' in request.query_params:

            month=request.query_params.get('month')

            qs=qs.filter(created_date__month=month)

        if 'year' in request.query_params:

            year=request.query_params.get('year')

            qs=qs.filter(created_date__year=year)
        

        if 'category' in request.query_params:

            category=request.query_params.get('category')

            qs=qs.filter(category=category)
        
        if 'priority' in request.query_params:

            priority=request.query_params.get('priority')

            qs=qs.filter(priority=priority)


        if len(request.query_params.keys())==0:

            current_month=timezone.now().month
            
            current_year=timezone.now().year

            qs=qs.filter(created_date__month=current_month,created_date__year=current_year) 

        serializer=ExpenseSerializer(qs,many=True)

        return Response(data=serializer.data)   
    
class ExpenseSummaryView(APIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def get(self,request,*args,**kwargs):

        if 'start_date' in request.query_params and 'end_date' in request.query_params:

            start_date=datetime.strptime(request.query_params.get('start_date'),'%Y-%m-%d').date()

            end_date=datetime.strptime(request.query_params.get("end_date"),'%Y-%m-%d').date()

            all_expenses=Expense.objects.filter(owner=request.user,created_date__range=(start_date,end_date))

        else:
            current_month=timezone.now().month
            current_year=timezone.now().year

            all_expenses=Expense.objects.filter(
                                                owner=request.user,
                                                created_date__month=current_month,
                                                created_date__year=current_year
                                                )
        
        total_expense=all_expenses.values('amount').aggregate(total=Sum('amount'))['total']

        category_summary=all_expenses.values('category').annotate(total=Sum('amount')).order_by('-total')

        priority_summary=all_expenses.values('priority').annotate(total=Sum('amount')).order_by('-total')


        data={
                'total_expense':total_expense,
                'category_summary':category_summary,
                'priority_summary':priority_summary
            }

        return Response(data=data)




class IncomeviewSet(ModelViewSet):
    queryset=Income.objects.all()
    serializer_class=IncomeSerializer
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[OwnerOnly]
    

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def list(self, request, *args, **kwargs):
        
        qs=Income.objects.filter(owner=request.user)

        if 'month' in request.query_params:

            month=request.query_params.get('month')

            qs=qs.filter(created_date__month=month)
        
        if 'year' in request.query_params:

            year=request.query_params.get('year')

            qs=qs.filter(created_date__year=year)

        if 'category' in request.query_params:

            category=request.query_params.get('category')

            qs=qs.filter(category=category)

        if len(request.query_params.keys())==0:

            current_month=timezone.now().month

            current_year=timezone.now().year

            qs=qs.filter(created_date__month=current_month,created_date__year=current_year)

        serializer=IncomeSerializer(qs,many=True)

        return Response(data=serializer.data)
    
class IncomeSummaryView(APIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def get(self,requeat,*args,**kwargs):

        current_month=timezone.now().month
        current_year=timezone.now().year

        all_income=Income.objects.filter(
                                            owner=requeat.user,
                                            created_date__month=current_month,
                                            created_date__year=current_year
                                            )
        
        total_income=all_income.values('amount').aggregate(total=Sum('amount'))["total"]

        category_summary=all_income.values('category').annotate(total=Sum('amount'))

        data={
            'total_income':total_income,
            'category_summary':category_summary
        }

        return Response(data=data)
    

    
    


