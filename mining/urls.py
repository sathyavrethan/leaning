from django.urls import path
from . import views

urlpatterns = [
path('mine_block', views.minerapi, name='miner_api'),
path('get_chain', views.getchain, name='chain_api'),
path('add_transaction', views.addtransactions, name='transaction_api'),
path('connect_node', views.connect_node, name='connect_node'),
path('replace_chain', views.replace_chain, name='replace_chain')
]
