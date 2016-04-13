from __future__ import absolute_import

from django import template
from django.conf import settings
from django.contrib import comments
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.comments import signals
from django.contrib.comments.views.utils import next_redirect, confirmation_view
from django.shortcuts import get_object_or_404, render_to_response
from django.views.decorators.csrf import csrf_protect


@csrf_protect
@login_required
def flag(request, comment_id, next=None):
    """
    Flags a comment. Confirmation on GET, action on POST.

    Templates: :template:`comments/flag.html`,
    Context:
        comment
            the flagged `comments.comment` object
    """
    comment = get_object_or_404(comments.get_model(), pk=comment_id, site__pk=settings.SITE_ID)

    # Flag on POST
    if request.method == 'POST':
        perform_flag(request, comment)
        return next_redirect(request, fallback=next or 'comments-flag-done',
            c=comment.pk)

    # Render a form on GET
    else:
        return render_to_response('comments/flag.html',
            {'comment': comment, "next": next},
            template.RequestContext(request)
        )

@csrf_protect
@permission_required("comments.can_moderate")
def delete(request, comment_id, next=None):
    """
    Deletes a comment. Confirmation on GET, action on POST. Requires the "can
    moderate comments" permission.

    Templates: :template:`comments/delete.html`,
    Context:
        comment
            the flagged `comments.comment` object
    """
    comment = get_object_or_404(comments.get_model(), pk=comment_id, site__pk=settings.SITE_ID)

    # Delete on POST
    if request.method == 'POST':
        # Flag the comment as deleted instead of actually deleting it.
        perform_delete(request, comment)
        return next_redirect(request, fallback=next or 'comments-delete-done',
            c=comment.pk)

    # Render a form on GET
    else:
        return render_to_response('comments/delete.html',
            {'comment': comment, "next": next},
            template.RequestContext(request)
        )

@csrf_protect
@permission_required("comments.can_moderate")
def approve(request, comment_id, next=None):
    """
    Approve a comment (that is, mark it as public and non-removed). Confirmation
    on GET, action on POST. Requires the "can moderate comments" permission.

    Templates: :template:`comments/approve.html`,
    Context:
        comment
            the `comments.comment` object for approval
    """
    comment = get_object_or_404(comments.get_model(), pk=comment_id, site__pk=settings.SITE_ID)

    # Delete on POST
    if request.method == 'POST':
        # Flag the comment as approved.
        perform_approve(request, comment)
        return next_redirect(request, fallback=next or 'comments-approve-done',
            c=comment.pk)

    # Render a form on GET
    else:
        return render_to_response('comments/approve.html',
            {'comment': comment, "next": next},
            template.RequestContext(request)
        )

# The following functions actually perform the various flag/aprove/delete
# actions. They've been broken out into separate functions to that they
# may be called from admin actions.

def perform_flag(request, comment):
    """
    Actually perform the flagging of a comment from a request.
    """
    flag, created = comments.models.CommentFlag.objects.get_or_create(
        comment = comment,
        user    = request.user,
        flag    = comments.models.CommentFlag.SUGGEST_REMOVAL
    )
    signals.comment_was_flagged.send(
        sender  = comment.__class__,
        comment = comment,
        flag    = flag,
        created = created,
        request = request,
    )

def perform_delete(request, comment):
    flag, created = comments.models.CommentFlag.objects.get_or_create(
        comment = comment,
        user    = request.user,
        flag    = comments.models.CommentFlag.MODERATOR_DELETION
    )
    comment.is_removed = True
    comment.save()
    signals.comment_was_flagged.send(
        sender  = comment.__class__,
        comment = comment,
        flag    = flag,
        created = created,
        request = request,
    )


def perform_approve(request, comment):
    flag, created = comments.models.CommentFlag.objects.get_or_create(
        comment = comment,
        user    = request.user,
        flag    = comments.models.CommentFlag.MODERATOR_APPROVAL,
    )

    comment.is_removed = False
    comment.is_public = True
    comment.save()

    signals.comment_was_flagged.send(
        sender  = comment.__class__,
        comment = comment,
        flag    = flag,
        created = created,
        request = request,
    )

# Confirmation views.

flag_done = confirmation_view(
    template = "comments/flagged.html",
    doc = 'Displays a "comment was flagged" success page.'
)
delete_done = confirmation_view(
    template = "comments/deleted.html",
    doc = 'Displays a "comment was deleted" success page.'
)
approve_done = confirmation_view(
    template = "comments/approved.html",
    doc = 'Displays a "comment was approved" success page.'
)
