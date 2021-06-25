from django.urls import path
from .views import ExpenseStats

urlpatterns=[
    path('expense_summary/', ExpenseStats.as_view(), name= 'expense_summary'),
]
