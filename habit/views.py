from django.shortcuts import render
from .models import *
from datetime import date, timedelta
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

# Create your views here.

def index(request):
    return render(request, "index.html")

@csrf_exempt
def habits_api(request):
    if request.method == 'GET':
        habits = Habit.objects.all()
        habits_data = []
        
        for habit in habits:
            today = timezone.now().date()
            try:
                today_completion = HabitCompletion.objects.get(habit=habit, date=today)
                completed_today = today_completion.completed
            except HabitCompletion.DoesNotExist:
                completed_today = False
            
            habits_data.append({
                'id': habit.id,
                'name': habit.name,
                'description': habit.description,
                'frequency': habit.frequency,
                'created_date': habit.created_date.strftime('%Y-%m-%d'),
                'completed_today': completed_today,
                'streak': calculate_streak(habit)
            })
        
        return JsonResponse({'habits': habits_data})
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            habit = Habit.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                frequency=data.get('frequency', 'daily')
            )
            
            return JsonResponse({
                'message': 'Habit created successfully',
                'habit': {
                    'id': habit.id,
                    'name': habit.name,
                    'description': habit.description,
                    'frequency': habit.frequency,
                    'created_date': habit.created_date.strftime('%Y-%m-%d')
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)



@csrf_exempt
def complete_habit(request, habit_id):
    if request.method == 'POST':
        try:
            habit = Habit.objects.get(id=habit_id)
            today = timezone.now().date()
            
            completion, created = HabitCompletion.objects.get_or_create(
                habit=habit,
                date=today
            )
            completion.completed = True
            completion.save()
            
            return JsonResponse({
                'message': 'Habit marked as completed',
                'streak': calculate_streak(habit)
            })
        except Habit.DoesNotExist:
            return JsonResponse({'error': 'Habit not found'}, status=404)


@csrf_exempt
def delete_habit(request, habit_id):
    if request.method == 'DELETE':
        try:
            habit = Habit.objects.get(id=habit_id)
            habit.delete()
            return JsonResponse({'message': 'Habit deleted successfully'})
        except Habit.DoesNotExist:
            return JsonResponse({'error': 'Habit not found'}, status=404)


def calculate_streak(habit):
    today = timezone.now().date()
    streak = 0
    current_date = today
    
    while True:
        try:
            completion = HabitCompletion.objects.get(habit=habit, date=current_date)
            if completion.completed:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        except HabitCompletion.DoesNotExist:
            break
    
    return streak


@csrf_exempt
def reports_api(request):
    if request.method == 'GET':
        report_type = request.GET.get('type', 'frequency')
        
        if report_type == 'frequency':
            return frequency_report(request)
        elif report_type == 'streaks':
            return streaks_report(request)
        elif report_type == 'completion-rate':
            return completion_rate_report(request)
        else:
            return JsonResponse({'error': 'Invalid report type'}, status=400)


def frequency_report(request):
    habits = Habit.objects.all()
    report_data = []
    
    for habit in habits:
        # Count completions in last 30 days
        start_date = timezone.now().date() - timedelta(days=30)
        completions = HabitCompletion.objects.filter(
            habit=habit, 
            date__gte=start_date, 
            completed=True
        ).count()
        
        report_data.append({
            'habit_name': habit.name,
            'completions_last_30_days': completions,
            'completion_rate': (completions / 30) * 100  
        })
    
    return JsonResponse({'frequency_report': report_data})

def streaks_report(request):
    habits = Habit.objects.all()
    report_data = []
    
    for habit in habits:
        current_streak = calculate_streak(habit)
        
        # Calculate longest streak (simplified)
        all_completions = HabitCompletion.objects.filter(habit=habit, completed=True).order_by('date')
        longest_streak = 0
        current_longest = 0
        prev_date = None
        
        for completion in all_completions:
            if prev_date is None or (completion.date - prev_date).days == 1:
                current_longest += 1
            else:
                current_longest = 1
            longest_streak = max(longest_streak, current_longest)
            prev_date = completion.date
        
        report_data.append({
            'habit_name': habit.name,
            'current_streak': current_streak,
            'longest_streak': longest_streak
        })
    
    return JsonResponse({'streaks_report': report_data})


def completion_rate_report(request):
    habits = Habit.objects.all()
    report_data = []
    
    for habit in habits:
        total_days = (timezone.now().date() - habit.created_date.date()).days + 1
        completed_days = HabitCompletion.objects.filter(habit=habit, completed=True).count()
        
        completion_rate = (completed_days / total_days * 100) if total_days > 0 else 0
        
        report_data.append({
            'habit_name': habit.name,
            'total_days': total_days,
            'completed_days': completed_days,
            'completion_rate': round(completion_rate, 2)
        })
    
    return JsonResponse({'completion_rate_report': report_data})