import numpy as np
import wikipedia, wikipediaapi
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import (TwoSidedFinancialTransaction, Entity, Era, Theme, Chain)


def finance_home(request):
    return render(request, 'finance/home.html')

def query(request):
    if request.method == "GET":
        term = request.GET.get('term', None)
        if term: # If term is not None.
            context = {'term': term}
            transactions_with_term_contained_in_entity_1 = TwoSidedFinancialTransaction.objects.filter(entity_1__contains=term).all()
            transactions_with_term_contained_in_entity_2 = TwoSidedFinancialTransaction.objects.filter(entity_2__contains=term).all()
            transactions_with_term_contained_in_description_of_asset_received_by_entity_1 = TwoSidedFinancialTransaction.objects.filter(description_of_asset_received_by_entity_1__contains=term).all()
            transactions_with_term_contained_in_description_of_asset_received_by_entity_2 = TwoSidedFinancialTransaction.objects.filter(description_of_asset_received_by_entity_2__contains=term).all()
            transactions_with_term_contained_in_description = TwoSidedFinancialTransaction.objects.filter(description__contains=term).all()
            transactions_with_term_contained_in_citation = TwoSidedFinancialTransaction.objects.filter(citation__contains=term).all()

            context.update({
                "transactions_with_term_contained_in_entity_1": np.array(transactions_with_term_contained_in_entity_1),
                "transactions_with_term_contained_in_entity_2": np.array(transactions_with_term_contained_in_entity_2),
                "transactions_with_term_contained_in_description_of_asset_received_by_entity_1": np.array(transactions_with_term_contained_in_description_of_asset_received_by_entity_1),
                "transactions_with_term_contained_in_description_of_asset_received_by_entity_2": np.array(transactions_with_term_contained_in_description_of_asset_received_by_entity_2),
                "transactions_with_term_contained_in_description": np.array(transactions_with_term_contained_in_description),
                "transactions_with_term_contained_in_citation": np.array(transactions_with_term_contained_in_citation),
            })

            print(transactions_with_term_contained_in_description_of_asset_received_by_entity_1)

            return render(request, 'finance/query.html', context)
    return render(request, 'base/index.html')


                                ####################


####################################################################################
####################################################################################
################################ BEGIN TRANSACTIONS ################################
####################################################################################
####################################################################################


class TransactionListView(ListView):
    model = TwoSidedFinancialTransaction
    template_name = 'finance/finance_list_view.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super(TransactionListView, self).get_context_data(**kwargs)
        context.update({"header": "Transactions", "title": "Transactions", "type": "transaction"})
        return context


class UserTransactionListView(ListView):
    model = TwoSidedFinancialTransaction
    template_name = 'finance/finance_list_view.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_queryset(self):
        """Get entries by specific user (as passed into URL)."""
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return TwoSidedFinancialTransaction.objects.filter(author=user).order_by('-date_entered')

    def get_context_data(self, **kwargs):
        context = super(UserTransactionListView, self).get_context_data(**kwargs)
        username=self.kwargs.get('username')
        context.update({"header": f"Transactions by {username}", "title": f"Transactions by {username}", "type": "transaction"})
        return context


class TransactionDetailView(UserPassesTestMixin, DetailView):
    model = TwoSidedFinancialTransaction
    template_name = 'finance/transactions/transaction_detail_view.html'
    context_object_name = 'transaction'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(TransactionDetailView, self).get_context_data(**kwargs)
        item = get_object_or_404(TwoSidedFinancialTransaction, id=self.kwargs.get('pk'))
        context.update({"title": f"Transaction: {item.description}", "type": "transaction"})
        return context


class TransactionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = TwoSidedFinancialTransaction
    fields = ['entity_1', 'type_of_asset_received_by_entity_1', 'description_of_asset_received_by_entity_1', 'monetary_value_of_asset_received_by_entity_1', 'monetary_value_of_asset_received_by_entity_1_is_estimated', 'currency_of_asset_received_by_entity_1_if_applicable', 'entity_2', 'type_of_asset_received_by_entity_2', 'description_of_asset_received_by_entity_2', 'monetary_value_of_asset_received_by_entity_2', 'monetary_value_of_asset_received_by_entity_2_is_estimated', 'currency_of_asset_received_by_entity_2_if_applicable', 'crime', 'description', 'entities', 'transaction_date', 'citation']
    template_name = 'views/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(TransactionCreateView, self).get_context_data(**kwargs)
        header = "Create transaction"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class TransactionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TwoSidedFinancialTransaction
    fields = ['entity_1', 'type_of_asset_received_by_entity_1', 'description_of_asset_received_by_entity_1', 'monetary_value_of_asset_received_by_entity_1', 'monetary_value_of_asset_received_by_entity_1_is_estimated', 'currency_of_asset_received_by_entity_1_if_applicable', 'entity_2', 'type_of_asset_received_by_entity_2', 'description_of_asset_received_by_entity_2', 'monetary_value_of_asset_received_by_entity_2', 'monetary_value_of_asset_received_by_entity_2_is_estimated', 'currency_of_asset_received_by_entity_2_if_applicable', 'crime', 'description', 'entities', 'transaction_date', 'citation']
    template_name = 'views/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        """
        Check that the user (who is logged in) that is trying to
        update the post is the same user that created the original
        post.
        """
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(TransactionUpdateView, self).get_context_data(**kwargs)
        header = "Update transaction"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class TransactionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TwoSidedFinancialTransaction
    success_url = '/' 
    context_object_name = 'item'
    template_name = 'views/confirm_delete.html'

    def test_func(self):
        """
        Check that the user (who is logged in) that is trying to
        delete the post is the same user that created the original
        post.
        """
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(TransactionDeleteView, self).get_context_data(**kwargs)
        transaction = get_object_or_404(TwoSidedFinancialTransaction, id=self.kwargs.get('pk'))
        title = f"Transaction: {transaction.description}"
        context.update({"type": "transaction", "title": title})
        return context


####################################################################################
####################################################################################
################################# END TRANSACTIONS #################################
####################################################################################
####################################################################################


                                ####################


####################################################################################
####################################################################################
################################## BEGIN ENTITIES ##################################
####################################################################################
####################################################################################


class EntityListView(ListView):
    model = Entity
    template_name = 'finance/finance_list_view.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super(EntityListView, self).get_context_data(**kwargs)
        context.update({"header": "Entities", "title": "Entities", "type": "entity"})
        return context


class UserEntityListView(ListView):
    model = Entity
    template_name = 'finance/finance_list_view.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_queryset(self):
        """Get entries by specific user (as passed into URL)."""
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Entity.objects.filter(author=user).order_by('-date_entered')

    def get_context_data(self, **kwargs):
        context = super(UserTransactionListView, self).get_context_data(**kwargs)
        username=self.kwargs.get('username')
        context.update({"header": f"Entities created by {username}", "title": f"Entities created by by {username}", "type": "entity"})
        return context


class EntityDetailView(UserPassesTestMixin, DetailView):
    model = Entity
    template_name = 'finance/entities/entity_detail_view.html'
    context_object_name = 'item'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        """Note: Try to search again for just "UBS." Throws a warning and doesn't show up on page due to warning. Fix this. ("Union Bank of Switzerland" works but not "UBS.")"""
        context = super(EntityDetailView, self).get_context_data(**kwargs)
        entity = get_object_or_404(Entity, id=self.kwargs.get('pk'))
        q = entity.title
        try:
            results = wikipedia.search(q, results=10, suggestion=True)
        except:
            try:    
                # suggestion = wikipedia.suggest(q) # Try to use exact query to get a suggestion.
                # print(suggestion)
                # results = wikipedia.search(suggestion, results=10, suggestion=False)
                results = wikipedia.search(q, results=10, suggestion=False) # Try to search for the exact term.
            except:
                results = None
            pass
        if results:
            try:
                first_result = results[0][0]
                pg = wikipedia.page(first_result)
                summary = wikipedia.summary(first_result)
                title = pg.title
                data = {
                    "results": results,
                    "summary": summary,
                    "error_msg": None,
                    "title": title,
                    "page_id": pg.pageid
                }
            except:
                data = {
                    "results": None,
                    "summ": None,
                    "error_msg": "No results found",
                    "title": None,
                    "page_id": None
                }
        
        context.update(data)

        return context

class EntityCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Entity
    fields = ['title', 'description']
    template_name = 'views/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(EntityCreateView, self).get_context_data(**kwargs)
        header = "Create entity"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class EntityUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Entity
    fields = ['title', 'description']
    template_name = 'views/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        """
        Check that the user (who is logged in) that is trying to
        update the post is the same user that created the original
        post.
        """
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(EntityUpdateView, self).get_context_data(**kwargs)
        header = "Update entity"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class EntityDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Entity
    success_url = '/' 
    context_object_name = 'item'
    template_name = 'views/confirm_delete.html'

    def test_func(self):
        """
        Check that the user (who is logged in) that is trying to
        delete the post is the same user that created the original
        post.
        """
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(EntityDeleteView, self).get_context_data(**kwargs)
        entity = get_object_or_404(Entity, id=self.kwargs.get('pk'))
        title = f"Entity: {entity.description}"
        context.update({"type": "entity", "title": title})
        return context


####################################################################################
####################################################################################
################################### END ENTITIES ###################################
####################################################################################
####################################################################################


                                ####################


####################################################################################
####################################################################################
################################### BEGIN CHAINS ###################################
####################################################################################
####################################################################################


class ChainListView(ListView):
    model = Chain
    template_name = 'finance/finance_list_view.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super(ChainListView, self).get_context_data(**kwargs)
        context.update({"header": "Chains", "title": "Chains", "type": "chain"})
        return context


class UserChainListView(ListView):
    model = Chain
    template_name = 'finance/finance_list_view.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_queryset(self):
        """Get entries by specific user (as passed into URL)."""
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Chain.objects.filter(author=user).order_by('-date_entered')

    def get_context_data(self, **kwargs):
        context = super(UserChainListView, self).get_context_data(**kwargs)
        username=self.kwargs.get('username')
        context.update({"header": f"Chains created by {username}", "title": f"Chains created by by {username}", "type": "chain"})
        return context


class ChainDetailView(UserPassesTestMixin, DetailView):
    model = Chain
    template_name = 'finance/finance_detail_view.html'
    context_object_name = 'item'

    def test_func(self):
        return self.request.user.is_authenticated


class ChainCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Chain
    fields = ['title', 'description']
    template_name = 'views/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(ChainCreateView, self).get_context_data(**kwargs)
        header = "Create chain"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class ChainUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Chain
    fields = ['title', 'description']
    template_name = 'views/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        """
        Check that the user (who is logged in) that is trying to
        update the post is the same user that created the original
        post.
        """
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(EntityUpdateView, self).get_context_data(**kwargs)
        header = "Update entity"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class ChainDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Chain
    success_url = '/' 
    context_object_name = 'item'
    template_name = 'views/confirm_delete.html'

    def test_func(self):
        """
        Check that the user (who is logged in) that is trying to
        delete the post is the same user that created the original
        post.
        """
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(ChainDeleteView, self).get_context_data(**kwargs)
        chain = get_object_or_404(Chain, id=self.kwargs.get('pk'))
        title = f"Chain: {chain.description}"
        context.update({"type": "chain", "title": title})
        return context


####################################################################################
####################################################################################
#################################### END CHAINS ####################################
####################################################################################
####################################################################################


                                ####################


####################################################################################
####################################################################################
#################################### BEGIN ERAS ####################################
####################################################################################
####################################################################################


class EraListView(ListView):
    model = Era
    template_name = 'finance/finance_list_view.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super(EraListView, self).get_context_data(**kwargs)
        context.update({"header": "Eras", "title": "Eras", "type": "era"})
        return context


class UserEraListView(ListView):
    model = Era
    template_name = 'finance/finance_list_view.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_queryset(self):
        """Get entries by specific user (as passed into URL)."""
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Era.objects.filter(author=user).order_by('-date_entered')

    def get_context_data(self, **kwargs):
        context = super(UserEraListView, self).get_context_data(**kwargs)
        username=self.kwargs.get('username')
        context.update({"header": f"Eras created by {username}", "title": f"Eras created by by {username}", "type": "era"})
        return context


class EraDetailView(UserPassesTestMixin, DetailView):
    model = Era
    template_name = 'finance/finance_detail_view.html'
    context_object_name = 'item'

    def test_func(self):
        return self.request.user.is_authenticated


class EraCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Era
    fields = ['title', 'description']
    template_name = 'views/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(EraCreateView, self).get_context_data(**kwargs)
        header = "Create era"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class EraUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Era
    fields = ['title', 'description']
    template_name = 'views/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        """
        Check that the user (who is logged in) that is trying to
        update the post is the same user that created the original
        post.
        """
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(EraUpdateView, self).get_context_data(**kwargs)
        header = "Update era"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class EraDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Era
    success_url = '/' 
    context_object_name = 'item'
    template_name = 'views/confirm_delete.html'

    def test_func(self):
        """
        Check that the user (who is logged in) that is trying to
        delete the post is the same user that created the original
        post.
        """
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(EraDeleteView, self).get_context_data(**kwargs)
        era = get_object_or_404(Era, id=self.kwargs.get('pk'))
        title = f"Era: {era.description}"
        context.update({"type": "era", "title": title})
        return context


####################################################################################
####################################################################################
##################################### END ERAS #####################################
####################################################################################
####################################################################################


                                ####################


####################################################################################
####################################################################################
################################### BEGIN THEMES ###################################
####################################################################################
####################################################################################


class ThemeListView(ListView):
    model = Theme
    template_name = 'finance/finance_list_view.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super(ThemeListView, self).get_context_data(**kwargs)
        context.update({"header": "Themes", "title": "Themes", "type": "theme"})
        return context


class UserThemeListView(ListView):
    model = Theme
    template_name = 'finance/finance_list_view.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_queryset(self):
        """Get entries by specific user (as passed into URL)."""
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Theme.objects.filter(author=user).order_by('-date_entered')

    def get_context_data(self, **kwargs):
        context = super(UserThemeListView, self).get_context_data(**kwargs)
        username=self.kwargs.get('username')
        context.update({"header": f"Themes created by {username}", "title": f"Themes created by by {username}", "type": "theme"})
        return context


class ThemeDetailView(UserPassesTestMixin, DetailView):
    model = Theme
    template_name = 'finance/finance_detail_view.html'
    context_object_name = 'item'

    def test_func(self):
        return self.request.user.is_authenticated


class ThemeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Theme
    fields = ['title', 'description']
    template_name = 'views/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(ThemeCreateView, self).get_context_data(**kwargs)
        header = "Create theme"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class ThemeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Theme
    fields = ['title', 'description']
    template_name = 'views/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        """
        Check that the user (who is logged in) that is trying to
        update the post is the same user that created the original
        post.
        """
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(ThemeUpdateView, self).get_context_data(**kwargs)
        header = "Update theme"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class ThemeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Theme
    success_url = '/' 
    context_object_name = 'item'
    template_name = 'views/confirm_delete.html'

    def test_func(self):
        """
        Check that the user (who is logged in) that is trying to
        delete the post is the same user that created the original
        post.
        """
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(ThemeDeleteView, self).get_context_data(**kwargs)
        theme = get_object_or_404(Theme, id=self.kwargs.get('pk'))
        title = f"Theme: {theme.description}"
        context.update({"type": "theme", "title": title})
        return context


####################################################################################
####################################################################################
#################################### END THEMES ####################################
####################################################################################
####################################################################################
