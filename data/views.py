from django.shortcuts import render


def d3_org_tree(request):
    return render(request, 'data/d3/org_tree.html')

def d3_tree_1(request):
    return render(request, 'data/d3/tree_1.html')

def d3_money_network(request):
    return render(request, 'data/d3/money_network.html')