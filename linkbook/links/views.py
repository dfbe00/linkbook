from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from linkbook.links.forms import LinkForm, BookForm, CommentForm
from linkbook.links.models import Link, Book, Comment

from taggit.models import Tag


def link(request, id):
    link = get_object_or_404(Link, id = id)
    comment_form = CommentForm()
    return render(request, 'links/link.html', 
        {'link': link, 'comment_form': comment_form})


def book(request, id):
    book = get_object_or_404(Book, id = id)
    links = book.link_set.all()
    return render(request, 'links/book.html', {'book': links})


@login_required
def create_link(request):
    if request.method == 'POST':
        form = LinkForm(request.user, request.POST)
        if form.is_valid():
            link = Link()
            link.user = request.user
            link.url = form.cleaned_data.get('url')
            link.title = form.cleaned_data.get('title')
            link.description = form.cleaned_data.get('description')
            link.save()
            tag_list = form.cleaned_data.get('tags')
            for tag in tag_list:
                link.tags.add(tag)
            link.books = form.cleaned_data.get('books')
            link.save()
            print("Done")
            return redirect('/')
    else:
        form = LinkForm(request.user)#initial = {'books': Book.objects.filter(user = request.user)})
        return render(request, 'links/new_link.html', {'form': form})


def edit_link(request, id):
    if request.method == 'POST':
        form = LinkForm(request.user, request.POST)
        if form.is_valid():
            link = Link.objects.get(id = id)
            link.user = request.user
            link.url = form.cleaned_data.get('url')
            link.title = form.cleaned_data.get('title')
            link.description = form.cleaned_data.get('description')
            link.save()
            link.tags.clear()
            tag_list = form.cleaned_data.get('tags')
            for tag in tag_list:
                link.tags.add(tag)
            link.books = form.cleaned_data.get('books')
            link.save()
            return redirect("/link/{}/".format(id))
    else:
        old_link = get_object_or_404(Link, id = id)
        initial_dict = {'url': old_link.url, 'title': old_link.title,
                   'description': old_link.description,
                   'tags': ", ".join(tag.name for tag in old_link.tags.all()),
                   'books': old_link.books.all()}
        print(old_link.description)
        form = LinkForm(request.user, initial = initial_dict)
        return render(request, 'links/edit_link.html', 
            {'form': form, 'link':old_link, 'color':'red'})


@login_required
def create_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = Book()
            book.user = request.user
            book.title = form.cleaned_data.get('title')
            book.description = form.cleaned_data.get('description')
            book.save()
            return redirect('/')
    else:
        form = BookForm()
        return render(request, 'links/new_book.html', {'form': form})

@login_required
def view_books(request):
    user_records = Book.objects.filter(user = request.user)
    return render(request, 'links/view_books.html', {'view_books':user_records})


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
