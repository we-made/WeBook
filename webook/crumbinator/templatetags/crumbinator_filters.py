from django import template
from django.template import Context
from django.template.loader import get_template
from anytree import Node, RenderTree

register = template.Library()


@register.filter(name="crumbinator")
def crumbinator(tree: Node):
    unpacked_tree = list()
    for pre, fill, node in RenderTree(tree):
        unpacked_tree.append(node)
    
    unpacked_tree[len(unpacked_tree) - 1].is_active = True

    ctx = Context(
        {
            "tree": unpacked_tree
        }
    ).flatten()
    template = get_template("mdbootstrap_crumbs.html")
    return template.render(ctx)