from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Animal, Especie, Raca, Medicacao

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Usuário ou senha inválidos")
    return render(request, "petguard/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")

@login_required(login_url="login")
def index(request):
    query = request.GET.get('q', '')
    especie_id = request.GET.get('especie')
    raca_id = request.GET.get('raca')
    status = request.GET.get('status')

    animais = Animal.objects.all()

    if query:
        animais = animais.filter(apelido__icontains=query)
    if especie_id and especie_id.lower() != 'todas as espécies':
        animais = animais.filter(especie_id=especie_id)
    if raca_id and raca_id.lower() != 'todas as raças':
        try:
            animais = animais.filter(raca_id=int(raca_id))
        except ValueError:
            pass
    if status and status.lower() != 'todos':
        animais = animais.filter(status=status)

    user = request.user
    grupos = [g.name for g in user.groups.all()]

    context = {
        'animais': animais,
        'especies': Especie.objects.all(),
        'racas': Raca.objects.all(),
        'is_admin': user.is_superuser,
        'is_operador': 'Operador' in grupos,
        'is_veterinario': 'Veterinario' in grupos,
    }

    return render(request, 'petguard/index.html', context)

@login_required(login_url="login")
def add_animal(request, id=None):
    user = request.user
    grupos = [g.name for g in user.groups.all()]

    if 'Veterinario' in grupos and not user.is_superuser:
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    animal = None
    if id:
        animal = get_object_or_404(Animal, id=id)

    especies = Especie.objects.all()
    racas = Raca.objects.all()

    if request.method == 'POST':
        anos = request.POST.get('anos')
        meses = request.POST.get('meses')
        apelido = request.POST.get('apelido')
        especie_id = request.POST.get('especie')
        raca_id = request.POST.get('raca')
        nova_raca_nome = request.POST.get('nova_raca')
        status = request.POST.get('status')
        observacoes = request.POST.get('observacoes')
        foto = request.FILES.get('foto')

        especie = get_object_or_404(Especie, id=especie_id)

        if nova_raca_nome:
            raca, _ = Raca.objects.get_or_create(nome=nova_raca_nome, especie=especie)
        elif raca_id:
            raca = get_object_or_404(Raca, id=raca_id)
        else:
            raca = None

        if animal:
            animal.anos = anos
            animal.meses = meses
            animal.apelido = apelido
            animal.especie = especie
            animal.raca = raca
            animal.status = status
            animal.observacoes = observacoes
            if foto:
                animal.foto = foto
            animal.save()
        else:
            Animal.objects.create(
                anos=anos,
                meses=meses,
                apelido=apelido,
                especie=especie,
                raca=raca,
                status=status,
                observacoes=observacoes,
                foto=foto,
            )

        return redirect('index')

    anos = range(0, 11)
    meses = range(0, 13)

    return render(request, 'petguard/addAnimal.html', {
        'animal': animal,
        'anos': anos,
        'meses': meses,
        'especies': especies,
        'racas': racas,
    })

@require_POST
@login_required(login_url="login")
def excluir_animal(request, animal_id):
    user = request.user
    grupos = [g.name for g in user.groups.all()]

    if 'Veterinario' in grupos and not user.is_superuser:
        return JsonResponse({"success": False, "error": "Sem permissão para excluir."})

    try:
        animal = Animal.objects.get(id=animal_id)
        animal.delete()
        return JsonResponse({"success": True})
    except Animal.DoesNotExist:
        return JsonResponse({"success": False, "error": "Animal não encontrado"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

@login_required
def perfil(request):
    user = request.user

    if request.method == "POST":
        nome = request.POST.get("name")
        telefone = request.POST.get("phone")
        email = request.POST.get("email")

        user.first_name = nome
        user.email = email
        user.save()

        if hasattr(user, "profile"):
            user.profile.telefone = telefone
            user.profile.save()

        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect("index")

    return render(request, "petguard/perfil.html", {"user": user})

@login_required(login_url="login")
def detalhes(request, id):
    animal = get_object_or_404(Animal, id=id)
    return render(request, "petguard/detalhes.html", {"animal": animal})

def racas_por_especie(request, especie_id):
    racas = Raca.objects.filter(especie_id=especie_id).values('id', 'nome')
    return JsonResponse(list(racas), safe=False)


@login_required(login_url="login")
def veterinario_view(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)
    medicacoes = animal.medicacoes.all().order_by('-data_aplicacao')

    if request.method == "POST":
        nome = request.POST.get('nome')
        observacoes = request.POST.get('observacoes')

        if nome:
            Medicacao.objects.create(
                animal=animal,
                nome=nome,
                observacoes=observacoes,
                data_aplicacao=timezone.now()
            )
        return redirect('veterinario', animal_id=animal.id)

    return render(request, 'petguard/veterinario.html', {
        'animal': animal,
        'medicacoes': medicacoes,
    })
