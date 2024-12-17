from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django_filters import FilterSet, DateFilter, CharFilter, ModelChoiceFilter
from django_filters.views import FilterView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserBlogCreationForm
from django.core.paginator import Paginator

class FormServicosFilter(FilterSet):
    nome = CharFilter(lookup_expr='icontains', label='Nome',
                      widget=forms.TextInput(
            attrs={
                'class': 'form-control',  
            }
        ),
    )
    data = DateFilter(field_name='data', lookup_expr='exact', label='Data',
                       widget=forms.DateInput(
            attrs={
                'type': 'date',  
                'class': 'form-control', 
            }
        ),
    )
    servico = ModelChoiceFilter(queryset=Servicos.objects.all(), label='Serviço', 
                                widget=forms.Select(
            attrs={
                'class': 'form-control', 
            }
        ),
    )

    class Meta:
        model = FormServicos
        fields = ['nome', 'servico', 'data']

class FormServicosListView(FilterView):
    model = FormServicos
    filtersetclass = FormServicosFilter

def pedidos(request): #READ
    form_list = FormServicos.objects.all()
    paginator = Paginator(form_list, 3) 
    
    page_number = request.GET.get('page')
    form = paginator.get_page(page_number)
    
    return render(request, 'pedidos.html', context={'form': form})

def cadastrar(request): #CREATE
    if request.method == 'POST':
        form = formulario(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('sasa:pedidos')
    else:
        form = formulario()
    context = {
        'form': form
    }
    return render(request, 'contato.html', context)
    
def administrador(request):
    
    filter = FormServicosFilter(request.GET, queryset=FormServicos.objects.all())

    filtered_queryset = filter.qs
    
    pendentes = filtered_queryset.filter(aceita=None)  
    aceitas = filtered_queryset.filter(aceita=True)    
    recusadas = filtered_queryset.filter(aceita=False)

    return render(request, 'administrador.html', context={'filter': filter, 'pendentes': pendentes, 'aceitas': aceitas, 'recusadas': recusadas})

@login_required
def inicio(request):
    carros = Carro.objects.all().order_by('nome')
    form = Procurarcarro(request.GET or None)
    if form.is_valid():
        nome = form.cleaned_data.get('nome')
        if nome:
            carros = Carro.objects.filter(nome__icontains=nome)
            
    return render(request, 'index.html', {'carros': carros, 'form': form})

def editar(request, id): #UPDATE
    formularios = FormServicos.objects.get(id=id)
    
    if request.method == "POST":
        form = formulario(request.POST, instance=formularios)
        if form.is_valid():
            form.save()
            return redirect('sasa:pedidos')
    else:
        form = formulario(instance=formularios)
    
    return render(request, 'contato.html', context={'form': form})

def deletar(request, id): #DELETE
    form = FormServicos.objects.get(id=id)
    form.delete()
    return redirect('sasa:pedidos')

def aceitar_servico(request, id):
    servico = get_object_or_404(FormServicos, pk=id)
    servico.aceita = True  
    servico.save()
    return redirect('sasa:administrador')  

def recusar_servico(request, id):
    servico = get_object_or_404(FormServicos, pk=id)
    servico.aceita = False  
    servico.save()
    return redirect('sasa:administrador')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('sasa:index')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('sasa:login')

def register(request):
    if request.method == 'POST':
        form = UserBlogCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro realizado com sucesso! Você já pode fazer login.')
            return redirect('sasa:login')
    else:
        form = UserBlogCreationForm()

    return render(request, 'register.html', {'form': form})