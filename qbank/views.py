from unicodedata import category
from django.shortcuts import render
from qbank.forms import ImportForm, ProfileForm,SignUpForm
from PyPDF2 import PdfReader
from django.views.generic import CreateView, UpdateView
import re
import io
import os
from .models import Category, ExamHeader,ExamQuestion, Profile, Project,Dashboard
from pikepdf import Pdf, PdfImage
from datetime import date
from django.conf import settings
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse_lazy


# Create your views here.

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'login.html'

def build_menu ():
    courses = ExamHeader.objects.all().order_by('category_ref', 'name')
    course_list = []
    menu_items = []
    prev_category =''
    category = {}
    for course in courses:
        if course.category_ref is not None:
            curr_category = course.category_ref.category_name
        else: 
            curr_category = 'Other'

        course_list.append({ "course_id" :  course.exam_id, "course_name" :course.name, "course_slug" : course.slug})

        if ( prev_category != curr_category and prev_category !='' ) : 
            category['category_name'] = prev_category
            category['course_list'] = course_list
            menu_items.append(category)
            course_list = []
            category = {}
        
        prev_category = curr_category
    
    if len(courses) > 0 :
        category['category_name'] = prev_category
        category['course_list'] = course_list
        menu_items.append(category)

    return menu_items

# Create your views here.
def login(request):
   menu_items = build_menu ()
   print (menu_items)
   course = ExamHeader.objects.all()[:3]
   return render(request, 'login.html', {"base_url" :settings.BASE_URL, "courses" : menu_items,"course_list" : course })
  
def home_view(request):
    menu_items = build_menu ()
    course = ExamHeader.objects.all()[:3]
    #projects = Project.objects.filter(auth_user_id=request.user.id).all()[:3]
    print("Menu items:", menu_items)
    print("Courses:", course)
    return render(request, "home.html", {"segment" :"index","base_url" :settings.BASE_URL, "courses" : menu_items, "course_list" : course})
    
def courses_view(request):
    menu_items = build_menu ()
    course = ExamHeader.objects.all()[:3]
    #projects = Project.objects.filter(auth_user_id=request.user.id).all()[:3]
    print("Menu items:", menu_items)
    print("Courses:", course)
    return render(request, "courses.html", {"segment" :"courses.html","base_url" :settings.BASE_URL, "courses" : menu_items, "course_list" : course})
    

def certificate_view(request, slug=""):
    course = ExamHeader.objects.filter(slug=slug).all().first()
    profile = Profile.objects.filter(auth_user_id=request.user.id).all().first()
    duration = settings.DEFAULT_FREE_QUUESTION_DURATION
    
    if request.user.is_authenticated and course.duration_m is not None : 
        duration = course.duration_m
    user_name = profile.first_name + " " +profile.first_name
    today = date.today()
    # print(today)
    # menu_items = build_menu ()
    return render(request, "certificate.html", {"base_url" :settings.BASE_URL, "course_title" : course.name, "course_duration" : duration, "user_name" : user_name, "today" : today})

def profile_view(request):
    menu_items = build_menu ()

    profile = Profile.objects.filter(auth_user_id=request.user.id).all().first()
    projects = Project.objects.filter(auth_user_id=request.user.id).all()
    print (request.user.id)
    if profile is not None:
        form = ProfileForm(instance=profile)
    else:
        form = ProfileForm()

    message = ""
    if request.method == "POST":
        if profile is not None:
            form = ProfileForm(request.POST,instance=profile)            
        else:
            form = ProfileForm(request.POST)
        if form.is_valid():
            print (request.POST.get('project_title'))
            if request.POST.get('project_title') != '' : 
                project = Project (project_title = request.POST.get('project_title'), auth_user_id =
                request.POST.get('auth_user_id'), duration = request.POST.get('auth_user_id'), 
                tech_stack = request.POST.get('tech_stack'), 
                project_description = request.POST.get('project_description'))
                project.save()
            
            form.save()
            message = "Saved Successfully !"
            # profile_info = form.save(commit=False)
            # profile_info.auth_user_id = request.user
            # profile_info.save()
            
    return render(request, "user_profile.html", {"base_url" :settings.BASE_URL, 
    "courses" : menu_items, 'form': form, "message" : message, 'projects' : projects })

def login_view(request):
    menu_items = build_menu ()
    course = ExamHeader.objects.all()[:3]
    return render(request, "login.html", {"base_url" :settings.BASE_URL, "courses" : menu_items,"course_list" : course  })

def dashboard_view(request):
    menu_items = build_menu ()
    dashboards = Dashboard.objects.filter(auth_user_id=request.user.id).all().order_by('date')
    
    # today = date.today()
    # is_pass = 'no'
    # if (total_correct > course.pass_score):
    #     is_pass = 'yes'

    return render(request, "dashboard.html", {"base_url" :settings.BASE_URL, "courses" : menu_items,
    "dashboards" : dashboards
      })

def catalogue_view(request):
    menu_items = build_menu ()
    return render(request, "catalogue.html", {"base_url" :settings.BASE_URL, "courses" : menu_items })
    


# def exampreview_view(request):
#     menu_items = build_menu ()
#     courses = ExamHeader.objects.filter
   
#     return render(request, "exam_preview.html", {"base_url" :settings.BASE_URL, "courses" : menu_items })
    
def exampreview_view(request, slug=""):
    menu_items = build_menu ()
    course = ExamHeader.objects.filter(slug=slug).all().first()

    duration = settings.DEFAULT_FREE_QUUESTION_DURATION
    
    if request.user.is_authenticated and course.duration_m is not None : 
        duration = course.duration_m


    return render(request, "exam_preview.html", {"base_url" :settings.BASE_URL, "courses" : menu_items , "course_desc" : course.desc, "course_title" : course.name, "course_keywords" : course.keywords,"course_slug" : course.slug, "course_duration" : duration, "course_pass_score" : course.pass_score })



def exam_view(request, slug=""):
    menu_items = build_menu ()
    
    

    #print (question_num)

    course = ExamHeader.objects.filter(slug=slug).all().first()
    questions = ExamQuestion.objects.filter(exam_ref=course).all().order_by('question_num')

    # print (len(questions))

    duration = settings.DEFAULT_FREE_QUUESTION_DURATION

    max_question = request.GET.get('max_question', len(questions))
    
    if request.user.is_authenticated and course.duration_m is not None : 
        duration = course.duration_m

    # print (questions[question_num+1])
    # print (question_num+1)
    # print(question_num-1)
    #return render(request, "exam.html", {"base_url" :settings.BASE_URL, "courses" : menu_items, "course_title" : course.name, "question_dtls" : questions[question_num], "total_question" : len(questions), "current_date" : course.date, "next_question" : question_num+1, "previous_question" : question_num-1, "course_slug" : course.slug})
    return render(request, "exam.html", {"base_url" :settings.BASE_URL, "courses" : menu_items, 
    "total_question" : max_question,  "course" : course,"duration" : duration
     })

def exam_question (request, slug="", question_num=1):
    
    course = ExamHeader.objects.filter(slug=slug).all().first()
    questions = ExamQuestion.objects.filter(exam_ref=course).all().order_by ('question_num')

    if not request.user.is_authenticated and question_num > settings.DEFAULT_FREE_QUUESTION :
        question_num =settings.DEFAULT_FREE_QUUESTION

    if not request.user.is_authenticated :
        max_question = settings.DEFAULT_FREE_QUUESTION
    else:
        request.session['max_question'] = int(request.GET.get('max_question', len(questions)))
        max_question = int(request.GET.get('max_question', len(questions)))
        #max_question = len(questions)

    print ("Max Question : " + str(max_question))

    if request.GET.get('is_next') == 'true' :
        print (request.GET.get('user_answer_'+str(course.exam_id)+'_'+str((question_num-1))))
        request.session['user_answer_'+str(course.exam_id)+'_'+str((question_num-1))] = request.GET.get('user_answer_'+str(course.exam_id)+'_'+str((question_num-1)))

    option_a ='false'
    option_b ='false'
    option_c ='false'
    option_d ='false'
    
    if 'user_answer_'+str(course.exam_id)+'_'+str((question_num)) in request.session and request.session['user_answer_'+str(course.exam_id)+'_'+str((question_num))] is not None:
        options = request.session['user_answer_'+str(course.exam_id)+'_'+str((question_num))].split(",")
        option_a = options[0].split("~")[1]
        option_b = options[1].split("~")[1]
        option_c = options[2].split("~")[1]
        option_d = options[3].split("~")[1]

    img_file = str(settings.BASE_DIR) + '/media/exam/inline-img-exam'+str(course.exam_id)+'-page'+str(question_num+1)+'-img0.png'
    print (img_file )

    if os.path.exists(img_file) : 
        img_file_exists = 'yes'
    else: 
        img_file_exists = 'no'
  
    # print (len(questions))

    # print (questions[question_num+1])
    # print (question_num+1)
    # print(question_num-1)
    #return render(request, "exam.html", {"base_url" :settings.BASE_URL, "courses" : menu_items, "course_title" : course.name, "question_dtls" : questions[question_num], "total_question" : len(questions), "current_date" : course.date, "next_question" : question_num+1, "previous_question" : question_num-1, "course_slug" : course.slug})
    return render(request, "exam_question.html", {"base_url" :settings.BASE_URL, 
    "question_dtls" : questions[question_num-1], 
    "max_question" : max_question,
    "course_slug" : course.slug, "course_id" : course.exam_id,
    'img_exists' : img_file_exists,
    'option_a' : option_a, 'option_b' : option_b, 'option_c' : option_c,
    'option_d' : option_d
})


def evaluate_exam(request,slug="", last_question=1):
    menu_items = build_menu ()
    course = ExamHeader.objects.filter(slug=slug).all().first()

    questions = ExamQuestion.objects.filter(exam_ref=course).all().order_by ('question_num')

    if request.GET.get('user_answer_'+str(course.exam_id)+'_'+str((last_question))) is not None : 
        request.session['user_answer_'+str(course.exam_id)+'_'+str((last_question))] = request.GET.get('user_answer_'+str(course.exam_id)+'_'+str((last_question)))

    if not request.user.is_authenticated : 
        MAX_QUESTION =settings.DEFAULT_FREE_QUUESTION
    else: 
        # MAX_QUESTION = len(questions)
        #MAX_QUESTION = int(request.GET.get('max_question', len(questions)))
        MAX_QUESTION  = request.session['max_question']
    ## ?? to be removed 
    #MAX_QUESTION =settings.DEFAULT_FREE_QUUESTION

    eval_question_list = []
    total_correct = 0
    
    for index, question in enumerate(questions):
        if (index+1) > MAX_QUESTION: break

        question_evaluation = {}

        question_evaluation ["question_dtl"] = question 
        
        multi_selection = False
        user_selection = ""
        if 'user_answer_'+str(course.exam_id)+'_'+str(question.question_num) in request.session :
            user_selected_val = request.session.get('user_answer_'+str(course.exam_id)+'_'+str(question.question_num), '')
            #print (user_selected_val)

            if user_selected_val is not None:
                user_choices = user_selected_val.split(",")
                #print (user_choices)
                if  user_choices[0].split("~")[1] == 'true' : 
                    user_selection ='A'
                    multi_selection = True
                if  user_choices[1].split("~")[1] == 'true' : 
                    if multi_selection : user_selection +=',B'
                    else: user_selection ='B'
                    multi_selection = True
                if  user_choices[2].split("~")[1] == 'true' : 
                    if multi_selection : user_selection +=',C'
                    else: user_selection ='C'
                    multi_selection = True
                if  user_choices[3].split("~")[1] == 'true' : 
                    if multi_selection : user_selection +=',D'
                    else: user_selection ='D'
                    multi_selection = True

        # print ("User selection : " + user_selection + ", correct answer : " + question.answer )

        is_answer_correct = 'false'
        if question.answer == user_selection : 
            is_answer_correct='true'
            total_correct = total_correct +1

        question_evaluation ["user_selection"] = user_selection
        question_evaluation ["is_answer_correct"] = is_answer_correct 


        eval_question_list.append(question_evaluation)

    is_pass = 'no'
    if (total_correct > course.pass_score):
        is_pass = 'yes'

    if request.GET.get('user_answer_'+str(course.exam_id)+'_'+str((last_question))) is not None and request.user.is_authenticated: 
        dashboard = Dashboard(auth_user_id=request.user.id,course_id=course, score_taken =total_correct,date = date.today() )
        dashboard.save()

    p = Paginator(eval_question_list, 1)  # creating a paginator object
    # getting the desired page number from url
    page_number = request.GET.get('page')
    try:
        question_obj = p.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        question_obj = p.page(1)
    except EmptyPage:
        # if page is empty then return last page
        question_obj = p.page(p.num_pages)

    #context = {'page_obj': page_obj}

    # print (question_obj.object_list)

    return render(request, "eval_report.html", {"base_url" :settings.BASE_URL,"course_name" :course.name,
    "courses" : menu_items ,"course_slug" :course.slug,
     'evaluation_report' : { "total_correct" :total_correct, "total_question" : MAX_QUESTION, 'is_pass' : is_pass,
     "questions" :  eval_question_list, 'question_obj': question_obj}   
     })
    
def reset_exam(request,slug=""):
    course = ExamHeader.objects.filter(slug=slug).all().first()
    questions = ExamQuestion.objects.filter(exam_ref=course).all().order_by ('question_num')

    if not request.user.is_authenticated : 
        MAX_QUESTION =settings.DEFAULT_FREE_QUUESTION
    else: 
        MAX_QUESTION = len(questions)
    ## ?? to be removed 
    MAX_QUESTION =settings.DEFAULT_FREE_QUUESTION

    for index, question in enumerate(questions):
        if (index+1) > MAX_QUESTION: break
        if 'user_answer_'+str(course.exam_id)+'_'+str(question.question_num) in request.session : 
            del request.session['user_answer_'+str(course.exam_id)+'_'+str(question.question_num)]
    
    return JsonResponse({'is_cleared':'cleared'})
 

def pdf_upload(request):
    
    def _parse_line(line):
        for key, rx in rx_dict.items():
            match = rx.search(line)
            if match:
                return key, match
        # if there are no matches
        return None, None

    if request.method == 'POST' : 
        form = ImportForm(request.POST or None)
        file = request.FILES['pdf_file']
        rx_dict = {
        'question_num': re.compile(r'QUESTION NO: (\d*)'),
        'A': re.compile(r'A\.'),
        'B': re.compile(r'B\.'),
        'C': re.compile(r'C\.'),
        'D': re.compile(r'D\.'),
        'E': re.compile(r'E\.'),
        'F': re.compile(r'F\.'),
        'answer': re.compile(r'Answer: (.*)'),
        'explanation': re.compile(r'Explanation:'),
        'reference': re.compile(r'Reference:(.*)'), 
        'page_num': re.compile(r'www.actualtests.com\s+(\d*)'), 
        }
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() +"\n"
        #print (text)
        text = text.replace("\"Pass Any Exam. Any Time.\"", "")
        #text = text.replace("www.actualtests.com", "")
        
        print ( "First Line : " + text.split('\n', 1)[0] ) 
        text = text.replace(text.split('\n', 1)[0] + " Exam", "")

        buffer = text.split ("\n")
        question =""
        A_option =""
        B_option =""
        C_option =""
        D_option =""
        E_option =""
        F_option =""
        answer =""
        reference = ""
        explanation =""
        is_question_on = False
        is_Aoption_on = False
        is_Boption_on = False
        is_Coption_on = False
        is_Doption_on = False
        is_Eoption_on = False
        is_Foption_on = False
        is_answer_on = False
        is_skip_off = True
        prev_question_num =""
        curr_question_num =""
        line_count = 0
        page_num = 0
        exam_header=None
        for line in buffer:
            key, match = _parse_line(line)
            line_count+=1
            if (line_count == 4): 
                slug = line.replace(" ", "_") + ".html"
                keywords = line.replace(" ", ",")

                exam_header =ExamHeader(name= line, desc = line, slug = slug, keywords=keywords)
                exam_header.save()
                exam_id = exam_header.exam_id
                print ( "Exam ID " + str(exam_id))


            if key == 'question_num':
                is_question_on = True
                curr_question_num = match.group(1)
                if  prev_question_num != '' and curr_question_num != prev_question_num : 
                    exam_question = ExamQuestion(question=question.strip(), option_a =A_option.strip(), 
                     option_b =B_option.strip(), option_c =C_option.strip(), option_d =D_option.strip(),option_e =E_option.strip(), 
                     option_f =F_option.strip(),answer =answer.strip(),referrence =reference.strip(), explanation = explanation.strip(), 
                     exam_ref =  exam_header, question_num=prev_question_num, page_num=page_num)
                    exam_question.save()
                    # print ( "\n\n" + "Question Number : "+ str(prev_question_num) + " : " + question + "\n\n")
                    # print ( "" +A_option )
                    # print ( "" +B_option )
                    # print ( "" +C_option )
                    # print ( "" +D_option )
                    # print ( "" +E_option )
                    # print ( " " +F_option )
                    # print ( "Answer " +answer )
                    # print ( "Reference " +reference )
                    is_Aoption_on = False
                    is_Boption_on = False
                    is_Coption_on = False
                    is_Doption_on = False
                    is_Eoption_on = False
                    is_Foption_on = False
                    question =""
                    A_option =""
                    B_option =""
                    C_option =""
                    D_option =""
                    E_option =""
                    F_option =""
                    reference =""
                    explanation =""
                prev_question_num = match.group(1)
            elif key == 'A':
                is_question_on = False
                is_Aoption_on = True
                is_Boption_on = False
            elif key == 'B':
                is_Aoption_on = False
                is_Boption_on = True
            elif key == 'C':
                is_Aoption_on = False
                is_Boption_on = False
                is_Coption_on = True
            elif key == 'D':
                is_Aoption_on = False
                is_Boption_on = False
                is_Coption_on = False
                is_Doption_on = True
            elif key == 'E':
                is_Aoption_on = False
                is_Boption_on = False
                is_Coption_on = False
                is_Doption_on = False
                is_Eoption_on = True
            elif key == 'F':
                is_Aoption_on = False
                is_Boption_on = False
                is_Coption_on = False
                is_Doption_on = False
                is_Eoption_on = False
                is_Foption_on = True
            elif key == 'answer':
                answer = match.group(1)
                is_Aoption_on = False
                is_Boption_on = False
                is_Coption_on = False
                is_Doption_on = False
                is_Eoption_on = False
                is_Foption_on = False
            elif key == 'reference':
                reference = match.group(1)
                is_Aoption_on = False
                is_Boption_on = False
                is_Coption_on = False
                is_Doption_on = False
                is_Eoption_on = False
                is_Foption_on = False
            elif key == 'page_num':
                page_num = match.group(1)
                is_skip_off = False
                
                
            if (is_skip_off and is_question_on and key!= 'question_num'): question+=line + "\n"
            elif (is_skip_off and is_Aoption_on and key!= 'A'): A_option+=line + "\n"
            elif (is_skip_off and is_Boption_on and key!= 'B'): B_option+=line + "\n"
            elif (is_skip_off and is_Coption_on and key!= 'C'): C_option+=line + "\n"
            elif (is_skip_off and is_Doption_on and key!= 'D'): D_option+=line + "\n"
            elif (is_skip_off and is_Eoption_on and key!= 'E'): E_option+=line + "\n"
            elif (is_skip_off and is_Foption_on and key!= 'F'): F_option+=line + "\n"

            is_skip_off = True

        #print (text)
        # last question 
        exam_question = ExamQuestion(question=question.strip(), option_a =A_option.strip(), 
                     option_b =B_option.strip(), option_c =C_option.strip(), option_d =D_option.strip(),option_e =E_option.strip(), 
                     option_f =F_option.strip(),answer =answer.strip(),referrence =reference.strip(), explanation = explanation.strip(), 
                     exam_ref =  exam_header, question_num=curr_question_num, page_num=page_num)
        exam_question.save()

        filename = 'inline-img'
        example = Pdf.open(file)

        for i, page in enumerate(example.pages):
            for j, (name, raw_image) in enumerate(page.images.items()):
                image = PdfImage(raw_image)
                out = image.extract_to(fileprefix=f"media/exam/{filename}-exam{exam_id}-page{(i+1)}-img{j}")
            # text = text.replace("\n", "")
        # text = text.replace("\r", "")
        # text = text.replace("\s", "")
        # text = text.replace("\t", "")
        #print (text)
        #q_patten = 'QUESTION NO: (\d*)'
        #q_list = re.compile(q_patten, re.MULTILINE).findall(text)
        #print (q_list)

        #q_patten = 'QUESTION NO: (.*)[?:\n\s\r]+(.*[\r\n\s].*[\r\n\s].*[\r\n\s].*[\r\n\s].*[\r\n\s].*[\r\n\s].*[\r\n\s].*?)'
        #q_patten = 'QUESTION NO: (.*)[?:\n\s\r]+()'


        #q_patten = 'QUESTION NO: (\d*)(.*)'
        #q_list = re.compile(q_patten, re.MULTILINE).findall(text)
        #print (q_list)


        #print ( re.findall( r'^QUESTION NO:(.*)QUESTION((?:\n.+)+)', text, re.MULTILINE) )
        #print (file.read())

        #file_data = file.read().decode("ut")
    
  

   
    
    else:
        form = ImportForm()

    return render(request, "import_pdf.html", {"form" : form})
