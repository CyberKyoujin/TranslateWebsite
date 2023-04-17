from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.generic import DeleteView
from .forms import UserForm
from django.contrib import messages
from .models import Translation, Wordbook
from django.db.models import Q

from decouple import config
import requests
import PyPDF2
import pytesseract
from reverso_context_api import Client
import deepl
import openai
from PIL import Image
from io import BytesIO

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# MAIN TTRANSLATOR

def index_page(request):
    if request.method == 'POST':
        if 'form1' in request.POST and request.FILES:
            file = request.FILES['file']
            language1 = request.POST.get('language1')
            language2 = request.POST.get('language2')
            selected_translator = request.POST.get('switch-one')
            converted = convert(file, language1)
            translated = translate(converted, language2, selected_translator)
            return render(request, 'index.html', {'converted': converted, 'translated': translated})
        elif 'form2' in request.POST:
            converted_text = request.POST.get('converted_text')
            translated_text = request.POST.get('translated_text')
            client = request.POST.get('client')
            if len(converted_text) > 0 and len(translated_text) > 0 and len(client) > 0:
                Translation.objects.create(user=request.user, client=client, text=converted_text, translation=translated_text)
                return redirect('translator_app:translations')
        else:
            return redirect('index')
    return render(request, 'index.html')

# USER LOGIC
       
def signup_page(request):
    user_form = UserForm()
    
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            password = user_form.cleaned_data['password1']
            username = user_form.cleaned_data['username']
             
            user.set_password(password)
            user.username = username
            user.save()
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('index')
            return HttpResponseRedirect(reverse('index'))
        else:
            print('Invalid form')
        
    user_form = UserForm()
    return render(request, 'registration/signup.html', {'user_form': user_form})     

def login_page(request):    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('index')
            else: 
                return messages.info(request,('User not active!')) 
        else:  
            print('pizda')
    return render(request, 'registration/login.html')    

@login_required
def user_logout(request):
    logout(request)
    return redirect('translator_app:login')

@login_required(login_url='translator_app:login')
def translation_page(request):
    translations = Translation.objects.filter(user=request.user).order_by('-date')
    return render(request, 'translations.html', {'translations': translations})

# TRANSLATIONS

class TranslationDelete(DeleteView):
    model = Translation
    template_name = 'translation_confirm_delete.html'
    success_url = reverse_lazy('translator_app:translations')
    
def translation_detail(request, pk):
    translate = get_object_or_404(Translation, pk=pk)
    if request.method == 'POST':
        
        client = request.POST.get('client')
        text = request.POST.get('text1')
        translation = request.POST.get('text2')
        
        translate.client = client
        translate.text = text
        translate.translation = translation
        translate.save()
        
    return render(request, 'translation_detail.html', {'object': translate})

# TRANSLATOR

def translator_page(request):
    if request.method == 'POST':
        if 'submit-1' in request.POST:
            text = request.POST.get('initial-text')
            language1 = request.POST.get('language1')
            translator = request.POST.get('switch-one')
            initial = ''.join(text)
            result = translate(initial, language1, translator)
            return render(request, 'translator.html', {'translation': result, 'initial': initial})
        if 'submit-2' in request.POST:
            text = request.POST.get('initial-text')
            translation = request.POST.get('text1')
            if len(text) > 0 and len(translation) > 1:
                initial = ''.join(text)
                client = request.POST.get('naming')
                save_to = request.POST.get('save')
            
                if save_to == 'translations':
                    Translation.objects.create(user=request.user, client=client, text=initial, translation=translation)
                    return redirect('translator_app:translations')
                elif save_to == 'wordbook':
                    Wordbook.objects.create(user=request.user, client=client, phrase=initial, translated=translation)
                    return redirect('translator_app:wordbook')
            else:
                return redirect('translator_app:translator')   
                
                          
    return render(request, 'translator.html')

            
# WORDBOOK

@login_required(login_url='translator_app:login')
def wordbook_page(request):
    if request.method == 'POST':
        word = request.POST.get('word')
        words = Wordbook.objects.filter(user=request.user).filter(Q(phrase__icontains=word) | Q(translated__icontains=word)).order_by('-date')
    else:
        words = Wordbook.objects.all().filter(user=request.user).order_by('-date')
    return render(request, 'wordbook.html', {'words': words})
 
class WordDeleteView(DeleteView):
    model = Wordbook
    template_name = 'word_confirm_delete.html'
    success_url = reverse_lazy('translator_app:wordbook')
    
    
def word_detail(request, pk):
    word = get_object_or_404(Wordbook, pk=pk)
    language1, language2 = detect_language(word.phrase), detect_language(word.translated)

    context = {'object': word, 'language1': language1, 'language2': language2, 'highlight_phrase': word.phrase}

    if request.method == 'POST':
        context_phrase = get_context_phrase(word.phrase, language1, language2)  
        print(word.phrase, language1, language2)
        context['context_phrase'] = context_phrase

    return render(request, 'word_detail.html', context)

# LOGIC FOR TRANSLATIONS bla bla

def convert(file, language1):
    file_extension = file.name.split('.')[-1]
    
    if file_extension in ['jpg', 'jpeg', 'png', 'bmp']:
        img = Image.open(BytesIO(file.read()))
        text = pytesseract.image_to_string(img, lang=language1[0:3])
        
    elif file_extension == 'pdf':
        pdf_reader = PyPDF2.PdfReader(file)
        page_count = len(pdf_reader.pages)
        text = ''
        for page in range(page_count):
            pdf_page = pdf_reader.pages[page]
            text += pdf_page.extract_text()
            
    else:
        text = 'Неподдерживаемый формат файла.'
        
    return text

def translate(text, language2, translator):
    if translator == 'gpt':
        openai.api_key = config('API_KEY1')
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{'role': 'user', 'content': 'Please:Translate this text or word into {language2}: {text}. In case if you can not carry out this translation or have another problem, just answer "Неправильный ввод. Попробуйте снова" without any further text'.format(text=text, language2=language2)}])
        return completion.choices[0].message.content
    elif translator == 'deepl':
        translator = deepl.Translator(config('API_KEY2'))
        return translator.translate_text(text, target_lang=language2[0:2].upper())
    
def detect_language(text):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {"client": "gtx", "sl": "auto", "tl": "en", "dt": "t", "q": text}
    response = requests.get(url, params=params)
    language_code = response.json()[2]
    return language_code
    
def get_context_phrase(phrase, lan1, lan2):
    client = Client(lan1, lan2)
    result = []
    counter = 0
    try:
        for context in client.get_translation_samples(phrase, cleanup=True):
            result.append((context))
            counter += 1
            if counter >= 3:
                break
    except requests.HTTPError as err:
        result = 0

    return result