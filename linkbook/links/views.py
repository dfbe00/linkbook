from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.contrib.auth.models import User

from linkbook.links.forms import LinkForm, BookForm, CommentForm
from linkbook.links.models import Link, Book, Comment

from taggit.models import Tag
from taggit.utils import _parse_tags
from .PyOpenGraph import PyOpenGraph

UP = 0
DOWN = 1
vote_color = "lighten-5"


def link(request, id):
    link = get_object_or_404(Link, id = id)
    comment_form = CommentForm()
    upvotes = link.votes.count(action = UP)
    downvotes = link.votes.count(action = DOWN)
    upvoted = link.votes.exists(request.user.id, action = UP)
    downvoted = link.votes.exists(request.user.id, action = DOWN)

    # open graph data
    show_og = True
    og = PyOpenGraph(link.url)
    
    if not og.is_valid:
        show_og = False
    elif og.image and og.image_height and og.image_width:
        ratio = int(og.image_height) / int(og.image_width)
        og.image_width = 150
        og.image_height = 150*ratio
    else:
        og.image_width = 150
        og.image_height = 150


    # upvote button config
    if not upvoted:
        upvote_button = ""
    else:
        upvote_button = vote_color

    # downvote button config
    if not downvoted:
        downvote_button = ""
    else:
        downvote_button = vote_color

    return render(request, 'links/link.html', 
        {'link': link, 'comment_form': comment_form, 'og': og, 'show_og': show_og,
        'upvotes': upvotes, 'downvotes': downvotes,
        'upvote_button': upvote_button, 'downvote_button': downvote_button})


def book(request, id):
    book = get_object_or_404(Book, id=id)
    links = book.link_set.all()
    return render(request, 'links/book.html', {'book': links})


@login_required
def create_link(request):
    if request.method == 'POST':
        link = Link()
        link.user = request.user
        link.url = request.POST.get('URL')
        link.title = request.POST.get('TITLE')
        link.description = request.POST.get('DESCRIPTION')
        link.save()
        tag_list = request.POST.get('TAGS')
        for tag in _parse_tags(tag_list):
            link.tags.add(tag)
        for book_name in request.POST.getlist('BOOKS'):
            link.books.add(Book.objects.get(user = request.user, title = book_name))
        link.save()
        return redirect('/link/{}/'.format(link.id))
    else:
        books = Book.objects.filter(user = request.user)
        return render(request, 'links/new_link.html', {'books': books})


@login_required
def edit_link(request, id):
    link = get_object_or_404(Link, id = id)
    books = Book.objects.filter(user = request.user)
    if request.method == 'POST':
        link.url = request.POST.get('URL')
        link.title = request.POST.get('TITLE')
        link.description = request.POST.get('DESCRIPTION')
        tag_list = request.POST.get('TAGS')
        for tag in _parse_tags(tag_list):
            link.tags.add(tag)

        new_book_list = request.POST.getlist('BOOKS')
        for book in books:
            if book in link.books.all() and book.title not in new_book_list:
                link.books.remove(book)
            elif book not in link.books.all() and book.title in new_book_list:
                link.books.add(book)
        link.save()
        return redirect('/link/{}/'.format(link.id))
    else:
        tag_text = ", ".join(tag.name for tag in link.tags.all())
        return render(request, 'links/edit_link.html', {'link':link, 'books': books, 'tag_text': tag_text})


@login_required
def vote_link(request, id):
    if request.method == 'GET':
        vote_type = request.GET['type']
        link = Link.objects.get(id = id)
        upvoted = link.votes.exists(request.user.id, action = UP)
        downvoted = link.votes.exists(request.user.id, action = DOWN)

        if vote_type == "U":
            if not upvoted:
                link.votes.up(request.user.id)
                link.save()
                upvote_button = vote_color
                downvote_button = ""
            else:
                link.votes.delete(request.user.id)
                link.save()
                upvote_button = ""
                downvote_button = ""
            return JsonResponse({'upvotes': link.votes.count(action = UP), 
                'downvotes': link.votes.count(action = DOWN),
                'upvote_button': upvote_button,
                'downvote_button': downvote_button})


        elif vote_type == "D":
            if not downvoted:
                link.votes.down(request.user.id)
                link.save()
                downvote_button = vote_color
                upvote_button = ""
            else:
                link.votes.delete(request.user.id)
                link.save()
                downvote_button = ""
                upvote_button = ""
            return JsonResponse({'upvotes': link.votes.count(action = UP),
                'downvotes': link.votes.count(action = DOWN),
                'upvote_button': upvote_button,
                'downvote_button': downvote_button})

        
@login_required
def create_book(request):
    if request.method == 'POST':
        book = Book()
        book.user = request.user
        book.title = request.POST.get('TITLE')
        book.description = request.POST.get('DESCRIPTION')
        book.save()
        return redirect('/')
    else:
        return render(request, 'links/new_book.html')


@login_required
def edit_book(request, id):
    book = get_object_or_404(Book, id = id)
    if request.method == 'POST':
        book.title = request.POST.get('TITLE')
        book.description = request.POST.get('DESCRIPTION')
        book.save()
        return redirect("/book/{}/".format(id))
    else:
        return render(request, 'links/edit_book.html', {'book':book})





@login_required
def create_comment(request, id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment()
            comment.user = request.user
            comment.link = Link.objects.get(id = id)
            comment.text = form.cleaned_data.get('text')
            comment.save()
            return redirect('/link/{}'.format(id))


@login_required
def view_tag(request, tag_name):
    tagged = Link.objects.filter(tags__name = tag_name)
    return render(request, "links/tags.html/", {'tag': tagged, 'tagname' : tag_name})