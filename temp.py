# UTTCex v5

# Karac Von Thweatt aka Father Crypto
# Under The Table Centralized Exchange Bot

import sys, json, interactions, requests, lib, hashlib, zlib, crypto, asyncio
import random, time, string, math, threading, qrcode, time, datetime, typing
import mysql.connector
import os, discord, math
import ulang, usql, udefs, ddefs, cmds, embeds, ulog, crypto

from fuzzywuzzy import process

from collections import defaultdict

from http.server import BaseHTTPRequestHandler, HTTPServer

from discord import Embed, Message

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import decimal
from decimal import Decimal

from discord.ext import tasks, commands
from discord.ui import *

import bitcoinlib
import web3
import monero
import xrpl
import solathon

from translation import *

from pycoingecko import CoinGeckoAPI
coingecko = CoinGeckoAPI()

newthread = threading.Thread

# 0 For main bot
# -1 For test bot
BOT_CFG_FLAG = -1

# Client
client = discord.Client(command_prefix="", intents=discord.Intents.all())
exenabled = True
esenabled = True
stenabled = False
lnenabled = False
waenabled = True
depenabled = True
fafenabled = False
wadepenabled = True
shutdown = False
active_discrepancy = False

reload_complete = False

# Channels
deposit_log_channel = 1158890527836618813

# MASTER WALLET IS CREATED, THIS IS THE NAME AND VARIABLE
btc_wallet = "BTC_MASTER"
ltc_wallet = "LTC_MASTER"
doge_wallet = "DOGE_MASTER"

# Coin & Rate List
coin_list = [["btc", 0.99],
             ["ltc", 0.99],
             ["doge", 0.98],
             ["eth", 0.98],
             #["usdc", 0.97],
             ["usdt", 0.97],
             #["shib", 0.95],
             #["pussy", 0.9],
             ["matic", 0.99],
             ["bnb", 0.99],
             #["busd", 0.97],
             #["cds", 0.96],
             #["op", 0.96],
             #["xrp", 0.99],
             ["sol", 0.99],
             ["fluffy", 0.97]]

sol_token_mint = {"fluffy": "F2cexxKrSsVk7XsQk1rBUV7UpLyDRU3eip1w6YCri37C"}

rate_dic = {"btc": Decimal("0.99"),
            "ltc": Decimal("0.99"),
            "doge": Decimal("0.98"),
            "eth": Decimal("0.98"),
            "usdc": Decimal("0.97"),
            "usdt": Decimal("0.97"),
            "shib": Decimal("0.95"),
            "pussy": Decimal("0.9"),
            "matic": Decimal("0.99"),
            "bnb": Decimal("0.99"),
            "busd": Decimal("0.97"),
            "cds": Decimal("0.96"),
            "op": Decimal("0.96"),
            "avax": Decimal("0.97"),
            "xrp": Decimal("0.99"),
            "xmr": Decimal("0.99"),
            "sol": Decimal("0.99"),
            "fluffy": Decimal("0.97")
            }

# Coin Atomic Conversion Dictionary
atomdic = {"btc": Decimal(str(0.00000001)),
           "ltc": Decimal(str(0.00000001)),
           "doge": Decimal(str(0.00000001)),
           "eth": Decimal(str(0.000000000000000001)),
           "usdc": Decimal(str(0.000001)),
           "usdt": Decimal(str(0.000001)),
           "shib": Decimal(str(0.000000000000000001)),
           "pussy": Decimal(str(0.000000000000000001)),
           "matic": Decimal(str(0.000000000000000001)),
           "pcds": Decimal(str(0.00000001)),
           "bnb": Decimal(str(0.000000000000000001)),
           "busd": Decimal(str(0.000000000000000001)),
           "cds": Decimal(str(0.00000001)),
           "op": Decimal(str(0.000000000000000001)),
           "avax": Decimal(str(0.000000000000000001)),
           "acds": Decimal(str(0.00000001)),
           "xrp": Decimal(str(0.000001)),
           "xmr": Decimal(str(0.000000000000001)),
           "sol": Decimal(str(0.000000001)),
           "fluffy": Decimal(str(0.00000001)),
           "uttc": Decimal(str(0.00000000001))
           }

decidic = {"cashmoney": ".12f",
           "btc": ".8f",
           "ltc": ".8f",
           "doge": ".8f",
           "eth": ".18f",
           "usdc": ".6f",
           "usdt": ".6f",
           "shib": ".18f",
           "pussy": ".18f",
           "matic": ".18f",
           "pcds": ".8f",
           "bnb": ".18f",
           "busd": ".18f",
           "cds": ".8f",
           "op": ".18f",
           "avax": ".18f",
           "acds": ".8f",
           "xrp": ".6f",
           "xmr": ".15f",
           "sol": ".9f",
           "fluffy": ".8f",
           "uttc": ".12f"
           }

bot_ids = {-1: {"tipcc": 617037497574359050, # Test bot IDs
                "uttcex": 1241891800075997224,
                "tipbot": 474841349968101386,
                "rabbitswap": 1242234800367206492
                },
           0: {"tipcc": 617037497574359050, # Main bot IDs
                "uttcex": 1057133315527815209,
                "tipbot": 474841349968101386,
                "rabbitswap": 1223368098816721017
                }
           }

bot_tokens = {-1: {"token": os.getenv("UVTB_TOKEN")},
              0: {"token": os.getenv("UDC_TOKEN")}
    }

emojis = {"uttc": "<:UTTC:1223166100821508126>",
          "btc": "<:BTC:892290576798605363>",
          "ltc": "<:LTC:1153895475670433873>",
          "doge": "<:DOGE:1153897726329749564>",
          "eth": "<:ETH:892290770600591381>",
          "usdc": "<:USDC:1159538765417684992>",
          "usdt": "<:USDT:1159686698410709104>",
          "shib": "<:SHIB:1159706104041848862>",
          "pussy": "<:PUSSY:1159946369872691251>",
          "matic": "<:MATIC:1158541816631668860>",
          "bnb": "<:BNB:892300158442811432>",
          "busd": "<:BUSD:1159625648852193300>",
          "cds": "<:CDS:1160557705342242826>",
          "op": "<:OP:1159608219421913210>",
          "xrp": "<:XRP:1159969638910791731>",
          "xmr": "<:XMR:1164855758681276456>",
          "sol": "<:SOL:1219898744619663360>",
          "fluffy": "<:FLUFFY:1220228529015488574>",
          "avax": "<:AVAX:1159621415931224115>"
          }

emojid = {"uttc": 1223166100821508126,
          "btc": 892290576798605363,
          "ltc": 1153895475670433873,
          "doge": 1153897726329749564,
          "eth": 892290770600591381,
          "usdc": 1159538765417684992,
          "usdt": 1159686698410709104,
          "shib": 1159706104041848862,
          "pussy": 1159946369872691251,
          "matic": 1158541816631668860,
          "bnb": 892300158442811432,
          "busd": 1159625648852193300,
          "cds": 1160557705342242826,
          "op": 1159608219421913210,
          "xrp": 1159969638910791731,
          "xmr": 1164855758681276456,
          "sol": 1219898744619663360,
          "fluffy": 1220228529015488574,
          "avax": 1159621415931224115
          }

alias = {"btc": "btc",
         "bitcoin": "btc",
         "sat": "btc",
         "sats": "btc",
         "satoshi": "btc",
         "satoshis": "btc",
         "ltc": "ltc",
         "litecoin": "ltc",
         "litoshi": "ltc",
         "litoshis": "ltc",
         "doge": "doge",
         "dogecoin": "doge",
         "d": "doge",
         "xmr": "xmr",
         "monero": "xmr",
         "piconero": "xmr",
         "piconeros": "xmr",
         "uttc": "uttc",
         "eth": "eth",
         "ethereum": "eth",
         "wei": "eth",
         "usdc": "usdc",
         "usdt": "usdt",
         "shib": "shib",
         "shibainu": "shib",
         "shibwei": "shib",
         "pussy": "pussy",
         "pussywei": "pussy",
         "matic": "matic",
         "polygon": "matic",
         "maticwei": "matic",
         "polywei": "matic",
         "bnb": "bnb",
         "bnbwei": "bnb",
         "busd": "busd",
         "busdwei": "busd",
         "cds": "cds",
         "op": "op",
         "opwei": "op",
         "avax": "avax",
         "avaxwei": "avax",
         "xrp": "xrp",
         "sol": "sol",
         "lamport": "sol",
         "lamports": "sol",
         "fluffy": "fluffy",
         "tuft": "fluffy",
         "tufts": "fluffy",
         }

chain_host = {"usdc": "eth",
              "usdt": "eth",
              "shib": "eth",
              "cds": "bnb",
              "pussy": "eth",
              "busd": "bnb",
              "fluffy": "sol"
              }

atomnames = ["sat", "sats", "satoshi", "satoshis", "litoshi", "litoshis", "wei", "shibwei", "pussywei", "maticwei",
             "polywei", "bnbwei", "busdwei", "opwei", "avaxwei", "lamport", "lamports", "tuft", "tufts"]

# CoinGecko
gcucoin_map = {"btc": "bitcoin",
               "ltc": "litecoin",
               "doge": "dogecoin",
               "eth": "ethereum",
               "usdc": "usd-coin",
               "usdt": "tether",
               "shib": "shiba-inu",
               "pussy": "pussy-financial",
               "matic": "matic-network",
               "bnb": "binancecoin",
               "busd": "binance-peg-busd",
               "cds": "crypto-development-services",
               "op": "optimism",
               "avax": "avalanche-2",
               "xrp": "ripple",
               "sol": "solana",
               "fluffy": "fluffy",
               "xmr": "monero"
               }

coincolor = {"btc": 0xffa200,
             "ltc": 0xc0bbbb,
             "doge": 0xe1b303,
             "eth": 0x3c3c3d,
             "usdc": 0x2775ca,
             "usdt": 0x26a17b,
             "shib": 0xf00500,
             "pussy": 0xcb33e6,
             "matic": 0x6d2f9e,
             "bnb": 0xf0b90b,
             "busd": 0xf0b90b,
             "cds": 0xc28917,
             "op": 0xff0420,
             "avax": 0xe84142,
             "xrp": 0x434c54,
             "sol": 0x00ffa3,
             "fluffy": 0x00aaff
             }

# Probably only for coins, not web3 tokens
uwallet = {"btc": btc_wallet,
           "ltc": ltc_wallet,
           "doge": doge_wallet
           }
# Probably only for coins, not web3 tokens
unetwork = {"btc": "bitcoin",
            "ltc": "litecoin",
            "doge": "dogecoin"
            }

web3network = {"eth": "https://mainnet.infura.io/v3/bb35bf5025e944478527884a6be25809",
               "usdc": "https://mainnet.infura.io/v3/bb35bf5025e944478527884a6be25809",
               "usdt": "https://mainnet.infura.io/v3/bb35bf5025e944478527884a6be25809",
               "shib": "https://mainnet.infura.io/v3/bb35bf5025e944478527884a6be25809",
               "pussy": "https://mainnet.infura.io/v3/bb35bf5025e944478527884a6be25809",
               "matic": "https://polygon-mainnet.infura.io/v3/bb35bf5025e944478527884a6be25809",
               "bnb": "https://bsc-dataseed.binance.org/",
               "cds": "https://bsc-dataseed.binance.org/",
               "op": "https://optimism-mainnet.infura.io/v3/bb35bf5025e944478527884a6be25809",
               "avax": "https://avalanche-mainnet.infura.io/v3/bb35bf5025e944478527884a6be25809"
               }

contract_addy = {"usdc": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                 "usdt": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                 "shib": "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce",
                 "pussy": "0x9196E18Bc349B1F64Bc08784eaE259525329a1ad",
                 "busd": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
                 "cds": "0x23f07a1C03e7C6D0C88e0E05E79B6E3511073fD5"
                 }

token_abi = {"usdc": [
                        {"constant": False, "inputs": [{"name": "newImplementation", "type": "address"}], "name": "upgradeTo",
                         "outputs": [], "payable": False, "stateMutability": "nonpayable", "type": "function"},
                        {"constant": False, "inputs": [{"name": "newImplementation", "type": "address"}, {"name": "data", "type": "bytes"}],
                         "name": "upgradeToAndCall", "outputs": [], "payable": True, "stateMutability": "payable", "type": "function"},
                        {"constant": True, "inputs": [], "name": "implementation", "outputs": [{"name": "", "type": "address"}],
                         "payable": False, "stateMutability": "view", "type": "function"},
                        {"constant": False, "inputs": [{"name": "newAdmin", "type": "address"}], "name": "changeAdmin", "outputs": [],
                         "payable": False, "stateMutability": "nonpayable", "type": "function"},
                        {"constant": True, "inputs": [], "name": "admin", "outputs": [{"name": "", "type": "address"}], "payable": False,
                         "stateMutability": "view", "type": "function"},
                        {"inputs": [{"name": "_implementation", "type": "address"}], "payable": False, "stateMutability": "nonpayable",
                         "type": "constructor"}, {"payable": True, "stateMutability": "payable", "type": "fallback"}, {"anonymous": False,
                                                                                                                       "inputs": [{
                                                                                                                                      "indexed": False,
                                                                                                                                      "name": "previousAdmin",
                                                                                                                                      "type": "address"},
                                                                                                                                  {
                                                                                                                                      "indexed": False,
                                                                                                                                      "name": "newAdmin",
                                                                                                                                      "type": "address"}],
                                                                                                                       "name": "AdminChanged",
                                                                                                                       "type": "event"},
                        {"anonymous": False, "inputs": [{"indexed": False, "name": "implementation", "type": "address"}],
                         "name": "Upgraded", "type": "event"}],
             "usdt": [{"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}],
                       "payable": False, "stateMutability": "view", "type": "function"},
                      {"constant": False, "inputs": [{"name": "_upgradedAddress", "type": "address"}],
                       "name": "deprecate", "outputs": [], "payable": False, "stateMutability": "nonpayable",
                       "type": "function"}, {"constant": False, "inputs": [{"name": "_spender", "type": "address"},
                                                                           {"name": "_value", "type": "uint256"}],
                                             "name": "approve", "outputs": [], "payable": False,
                                             "stateMutability": "nonpayable", "type": "function"},
                      {"constant": True, "inputs": [], "name": "deprecated", "outputs": [{"name": "", "type": "bool"}],
                       "payable": False, "stateMutability": "view", "type": "function"},
                      {"constant": False, "inputs": [{"name": "_evilUser", "type": "address"}], "name": "addBlackList",
                       "outputs": [], "payable": False, "stateMutability": "nonpayable", "type": "function"},
                      {"constant": True, "inputs": [], "name": "totalSupply",
                       "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view",
                       "type": "function"}, {"constant": False, "inputs": [{"name": "_from", "type": "address"},
                                                                           {"name": "_to", "type": "address"},
                                                                           {"name": "_value", "type": "uint256"}],
                                             "name": "transferFrom", "outputs": [], "payable": False,
                                             "stateMutability": "nonpayable", "type": "function"},
                      {"constant": True, "inputs": [], "name": "upgradedAddress",
                       "outputs": [{"name": "", "type": "address"}], "payable": False, "stateMutability": "view",
                       "type": "function"},
                      {"constant": True, "inputs": [{"name": "", "type": "address"}], "name": "balances",
                       "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view",
                       "type": "function"},
                      {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint256"}],
                       "payable": False, "stateMutability": "view", "type": "function"},
                      {"constant": True, "inputs": [], "name": "maximumFee",
                       "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view",
                       "type": "function"}, {"constant": True, "inputs": [], "name": "_totalSupply",
                                             "outputs": [{"name": "", "type": "uint256"}], "payable": False,
                                             "stateMutability": "view", "type": "function"},
                      {"constant": False, "inputs": [], "name": "unpause", "outputs": [], "payable": False,
                       "stateMutability": "nonpayable", "type": "function"},
                      {"constant": True, "inputs": [{"name": "_maker", "type": "address"}],
                       "name": "getBlackListStatus", "outputs": [{"name": "", "type": "bool"}], "payable": False,
                       "stateMutability": "view", "type": "function"},
                      {"constant": True, "inputs": [{"name": "", "type": "address"}, {"name": "", "type": "address"}],
                       "name": "allowed", "outputs": [{"name": "", "type": "uint256"}], "payable": False,
                       "stateMutability": "view", "type": "function"},
                      {"constant": True, "inputs": [], "name": "paused", "outputs": [{"name": "", "type": "bool"}],
                       "payable": False, "stateMutability": "view", "type": "function"},
                      {"constant": True, "inputs": [{"name": "who", "type": "address"}], "name": "balanceOf",
                       "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view",
                       "type": "function"},
                      {"constant": False, "inputs": [], "name": "pause", "outputs": [], "payable": False,
                       "stateMutability": "nonpayable", "type": "function"},
                      {"constant": True, "inputs": [], "name": "getOwner", "outputs": [{"name": "", "type": "address"}],
                       "payable": False, "stateMutability": "view", "type": "function"},
                      {"constant": True, "inputs": [], "name": "owner", "outputs": [{"name": "", "type": "address"}],
                       "payable": False, "stateMutability": "view", "type": "function"},
                      {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}],
                       "payable": False, "stateMutability": "view", "type": "function"}, {"constant": False, "inputs": [
                     {"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer",
                                                                                          "outputs": [],
                                                                                          "payable": False,
                                                                                          "stateMutability": "nonpayable",
                                                                                          "type": "function"},
                      {"constant": False, "inputs": [{"name": "newBasisPoints", "type": "uint256"},
                                                     {"name": "newMaxFee", "type": "uint256"}], "name": "setParams",
                       "outputs": [], "payable": False, "stateMutability": "nonpayable", "type": "function"},
                      {"constant": False, "inputs": [{"name": "amount", "type": "uint256"}], "name": "issue",
                       "outputs": [], "payable": False, "stateMutability": "nonpayable", "type": "function"},
                      {"constant": False, "inputs": [{"name": "amount", "type": "uint256"}], "name": "redeem",
                       "outputs": [], "payable": False, "stateMutability": "nonpayable", "type": "function"},
                      {"constant": True,
                       "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}],
                       "name": "allowance", "outputs": [{"name": "remaining", "type": "uint256"}], "payable": False,
                       "stateMutability": "view", "type": "function"},
                      {"constant": True, "inputs": [], "name": "basisPointsRate",
                       "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view",
                       "type": "function"},
                      {"constant": True, "inputs": [{"name": "", "type": "address"}], "name": "isBlackListed",
                       "outputs": [{"name": "", "type": "bool"}], "payable": False, "stateMutability": "view",
                       "type": "function"}, {"constant": False, "inputs": [{"name": "_clearedUser", "type": "address"}],
                                             "name": "removeBlackList", "outputs": [], "payable": False,
                                             "stateMutability": "nonpayable", "type": "function"},
                      {"constant": True, "inputs": [], "name": "MAX_UINT", "outputs": [{"name": "", "type": "uint256"}],
                       "payable": False, "stateMutability": "view", "type": "function"},
                      {"constant": False, "inputs": [{"name": "newOwner", "type": "address"}],
                       "name": "transferOwnership", "outputs": [], "payable": False, "stateMutability": "nonpayable",
                       "type": "function"},
                      {"constant": False, "inputs": [{"name": "_blackListedUser", "type": "address"}],
                       "name": "destroyBlackFunds", "outputs": [], "payable": False, "stateMutability": "nonpayable",
                       "type": "function"}, {
                          "inputs": [{"name": "_initialSupply", "type": "uint256"}, {"name": "_name", "type": "string"},
                                     {"name": "_symbol", "type": "string"}, {"name": "_decimals", "type": "uint256"}],
                          "payable": False, "stateMutability": "nonpayable", "type": "constructor"},
                      {"anonymous": False, "inputs": [{"indexed": False, "name": "amount", "type": "uint256"}],
                       "name": "Issue", "type": "event"},
                      {"anonymous": False, "inputs": [{"indexed": False, "name": "amount", "type": "uint256"}],
                       "name": "Redeem", "type": "event"},
                      {"anonymous": False, "inputs": [{"indexed": False, "name": "newAddress", "type": "address"}],
                       "name": "Deprecate", "type": "event"}, {"anonymous": False, "inputs": [
                     {"indexed": False, "name": "feeBasisPoints", "type": "uint256"},
                     {"indexed": False, "name": "maxFee", "type": "uint256"}], "name": "Params", "type": "event"},
                      {"anonymous": False, "inputs": [{"indexed": False, "name": "_blackListedUser", "type": "address"},
                                                      {"indexed": False, "name": "_balance", "type": "uint256"}],
                       "name": "DestroyedBlackFunds", "type": "event"},
                      {"anonymous": False, "inputs": [{"indexed": False, "name": "_user", "type": "address"}],
                       "name": "AddedBlackList", "type": "event"},
                      {"anonymous": False, "inputs": [{"indexed": False, "name": "_user", "type": "address"}],
                       "name": "RemovedBlackList", "type": "event"}, {"anonymous": False, "inputs": [
                     {"indexed": True, "name": "owner", "type": "address"},
                     {"indexed": True, "name": "spender", "type": "address"},
                     {"indexed": False, "name": "value", "type": "uint256"}], "name": "Approval", "type": "event"},
                      {"anonymous": False, "inputs": [{"indexed": True, "name": "from", "type": "address"},
                                                      {"indexed": True, "name": "to", "type": "address"},
                                                      {"indexed": False, "name": "value", "type": "uint256"}],
                       "name": "Transfer", "type": "event"},
                      {"anonymous": False, "inputs": [], "name": "Pause", "type": "event"},
                      {"anonymous": False, "inputs": [], "name": "Unpause", "type": "event"}],
             "shib": [{"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}],
                       "payable": False, "stateMutability": "view", "type": "function"}, {"constant": False, "inputs": [
                 {"name": "spender", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "approve",
                                                                                          "outputs": [{"name": "",
                                                                                                       "type": "bool"}],
                                                                                          "payable": False,
                                                                                          "stateMutability": "nonpayable",
                                                                                          "type": "function"},
                      {"constant": True, "inputs": [], "name": "totalSupply",
                       "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view",
                       "type": "function"}, {"constant": False, "inputs": [{"name": "sender", "type": "address"},
                                                                           {"name": "recipient", "type": "address"},
                                                                           {"name": "amount", "type": "uint256"}],
                                             "name": "transferFrom", "outputs": [{"name": "", "type": "bool"}],
                                             "payable": False, "stateMutability": "nonpayable", "type": "function"},
                      {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}],
                       "payable": False, "stateMutability": "view", "type": "function"}, {"constant": False, "inputs": [
                     {"name": "spender", "type": "address"}, {"name": "addedValue", "type": "uint256"}],
                                                                                          "name": "increaseAllowance",
                                                                                          "outputs": [{"name": "",
                                                                                                       "type": "bool"}],
                                                                                          "payable": False,
                                                                                          "stateMutability": "nonpayable",
                                                                                          "type": "function"},
                      {"constant": False, "inputs": [{"name": "value", "type": "uint256"}], "name": "burn",
                       "outputs": [], "payable": False, "stateMutability": "nonpayable", "type": "function"},
                      {"constant": True, "inputs": [{"name": "account", "type": "address"}], "name": "balanceOf",
                       "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view",
                       "type": "function"},
                      {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}],
                       "payable": False, "stateMutability": "view", "type": "function"}, {"constant": False, "inputs": [
                     {"name": "spender", "type": "address"}, {"name": "subtractedValue", "type": "uint256"}],
                                                                                          "name": "decreaseAllowance",
                                                                                          "outputs": [{"name": "",
                                                                                                       "type": "bool"}],
                                                                                          "payable": False,
                                                                                          "stateMutability": "nonpayable",
                                                                                          "type": "function"},
                      {"constant": False,
                       "inputs": [{"name": "recipient", "type": "address"}, {"name": "amount", "type": "uint256"}],
                       "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "payable": False,
                       "stateMutability": "nonpayable", "type": "function"}, {"constant": True, "inputs": [
                     {"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}], "name": "allowance",
                                                                              "outputs": [
                                                                                  {"name": "", "type": "uint256"}],
                                                                              "payable": False,
                                                                              "stateMutability": "view",
                                                                              "type": "function"}, {
                          "inputs": [{"name": "name", "type": "string"}, {"name": "symbol", "type": "string"},
                                     {"name": "decimals", "type": "uint8"}, {"name": "totalSupply", "type": "uint256"},
                                     {"name": "feeReceiver", "type": "address"},
                                     {"name": "tokenOwnerAddress", "type": "address"}], "payable": True,
                          "stateMutability": "payable", "type": "constructor"}, {"anonymous": False, "inputs": [
                     {"indexed": True, "name": "from", "type": "address"},
                     {"indexed": True, "name": "to", "type": "address"},
                     {"indexed": False, "name": "value", "type": "uint256"}], "name": "Transfer", "type": "event"},
                      {"anonymous": False, "inputs": [{"indexed": True, "name": "owner", "type": "address"},
                                                      {"indexed": True, "name": "spender", "type": "address"},
                                                      {"indexed": False, "name": "value", "type": "uint256"}],
                       "name": "Approval", "type": "event"}],
             "pussy": [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"anonymous": False,
                                                                                                "inputs": [
                                                                                                    {"indexed": True,
                                                                                                     "internalType": "address",
                                                                                                     "name": "owner",
                                                                                                     "type": "address"},
                                                                                                    {"indexed": True,
                                                                                                     "internalType": "address",
                                                                                                     "name": "spender",
                                                                                                     "type": "address"},
                                                                                                    {"indexed": False,
                                                                                                     "internalType": "uint256",
                                                                                                     "name": "value",
                                                                                                     "type": "uint256"}],
                                                                                                "name": "Approval",
                                                                                                "type": "event"},
                       {"anonymous": False, "inputs": [
                           {"indexed": True, "internalType": "address", "name": "previousOwner", "type": "address"},
                           {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}],
                        "name": "OwnershipTransferred", "type": "event"}, {"anonymous": False, "inputs": [
                     {"indexed": False, "internalType": "address", "name": "account", "type": "address"}],
                                                                           "name": "Paused", "type": "event"},
                       {"anonymous": False,
                        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"},
                                   {"indexed": True, "internalType": "bytes32", "name": "previousAdminRole",
                                    "type": "bytes32"},
                                   {"indexed": True, "internalType": "bytes32", "name": "newAdminRole",
                                    "type": "bytes32"}], "name": "RoleAdminChanged", "type": "event"},
                       {"anonymous": False,
                        "inputs": [{"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"},
                                   {"indexed": True, "internalType": "address", "name": "account", "type": "address"},
                                   {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}],
                        "name": "RoleGranted", "type": "event"}, {"anonymous": False, "inputs": [
                     {"indexed": True, "internalType": "bytes32", "name": "role", "type": "bytes32"},
                     {"indexed": True, "internalType": "address", "name": "account", "type": "address"},
                     {"indexed": True, "internalType": "address", "name": "sender", "type": "address"}],
                                                                  "name": "RoleRevoked", "type": "event"},
                       {"anonymous": False,
                        "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"},
                                   {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
                                   {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}],
                        "name": "Transfer", "type": "event"}, {"anonymous": False, "inputs": [
                     {"indexed": False, "internalType": "address", "name": "account", "type": "address"}],
                                                               "name": "Unpaused", "type": "event"},
                       {"inputs": [], "name": "DEFAULT_ADMIN_ROLE",
                        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
                        "stateMutability": "view", "type": "function"}, {
                           "inputs": [{"internalType": "address", "name": "owner", "type": "address"},
                                      {"internalType": "address", "name": "spender", "type": "address"}],
                           "name": "allowance", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                           "stateMutability": "view", "type": "function"}, {
                           "inputs": [{"internalType": "address", "name": "spender", "type": "address"},
                                      {"internalType": "uint256", "name": "amount", "type": "uint256"}],
                           "name": "approve", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                           "stateMutability": "nonpayable", "type": "function"},
                       {"inputs": [{"internalType": "address", "name": "account", "type": "address"}],
                        "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                        "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "decimals", "outputs": [
                     {"internalType": "uint8", "name": "", "type": "uint8"}], "stateMutability": "view",
                                                                         "type": "function"}, {
                           "inputs": [{"internalType": "address", "name": "spender", "type": "address"},
                                      {"internalType": "uint256", "name": "subtractedValue", "type": "uint256"}],
                           "name": "decreaseAllowance",
                           "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                           "stateMutability": "nonpayable", "type": "function"},
                       {"inputs": [{"internalType": "bytes32", "name": "role", "type": "bytes32"}],
                        "name": "getRoleAdmin", "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
                        "stateMutability": "view", "type": "function"}, {
                           "inputs": [{"internalType": "bytes32", "name": "role", "type": "bytes32"},
                                      {"internalType": "address", "name": "account", "type": "address"}],
                           "name": "grantRole", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {
                           "inputs": [{"internalType": "bytes32", "name": "role", "type": "bytes32"},
                                      {"internalType": "address", "name": "account", "type": "address"}],
                           "name": "hasRole", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                           "stateMutability": "view", "type": "function"}, {
                           "inputs": [{"internalType": "address", "name": "spender", "type": "address"},
                                      {"internalType": "uint256", "name": "addedValue", "type": "uint256"}],
                           "name": "increaseAllowance",
                           "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                           "stateMutability": "nonpayable", "type": "function"}, {"inputs": [], "name": "name",
                                                                                  "outputs": [{"internalType": "string",
                                                                                               "name": "",
                                                                                               "type": "string"}],
                                                                                  "stateMutability": "view",
                                                                                  "type": "function"},
                       {"inputs": [], "name": "owner",
                        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                        "stateMutability": "view", "type": "function"},
                       {"inputs": [], "name": "pause", "outputs": [], "stateMutability": "nonpayable",
                        "type": "function"}, {"inputs": [], "name": "paused",
                                              "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                                              "stateMutability": "view", "type": "function"},
                       {"inputs": [], "name": "renounceOwnership", "outputs": [], "stateMutability": "nonpayable",
                        "type": "function"}, {"inputs": [{"internalType": "bytes32", "name": "role", "type": "bytes32"},
                                                         {"internalType": "address", "name": "account",
                                                          "type": "address"}], "name": "renounceRole", "outputs": [],
                                              "stateMutability": "nonpayable", "type": "function"}, {
                           "inputs": [{"internalType": "bytes32", "name": "role", "type": "bytes32"},
                                      {"internalType": "address", "name": "account", "type": "address"}],
                           "name": "revokeRole", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
                       {"inputs": [{"internalType": "bytes4", "name": "interfaceId", "type": "bytes4"}],
                        "name": "supportsInterface", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                        "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "symbol", "outputs": [
                     {"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view",
                                                                         "type": "function"},
                       {"inputs": [], "name": "totalSupply",
                        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                        "stateMutability": "view", "type": "function"}, {
                           "inputs": [{"internalType": "address", "name": "recipient", "type": "address"},
                                      {"internalType": "uint256", "name": "amount", "type": "uint256"}],
                           "name": "transfer", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                           "stateMutability": "nonpayable", "type": "function"}, {
                           "inputs": [{"internalType": "address", "name": "sender", "type": "address"},
                                      {"internalType": "address", "name": "recipient", "type": "address"},
                                      {"internalType": "uint256", "name": "amount", "type": "uint256"}],
                           "name": "transferFrom", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                           "stateMutability": "nonpayable", "type": "function"},
                       {"inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}],
                        "name": "transferOwnership", "outputs": [], "stateMutability": "nonpayable",
                        "type": "function"},
                       {"inputs": [], "name": "unpause", "outputs": [], "stateMutability": "nonpayable",
                        "type": "function"}],
             "busd": [{"inputs": [], "payable": False, "stateMutability": "nonpayable", "type": "constructor"},
                      {"anonymous": False,
                       "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"},
                                  {"indexed": True, "internalType": "address", "name": "spender", "type": "address"},
                                  {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}],
                       "name": "Approval", "type": "event"}, {"anonymous": False, "inputs": [
                     {"indexed": True, "internalType": "address", "name": "previousOwner", "type": "address"},
                     {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}],
                                                              "name": "OwnershipTransferred", "type": "event"},
                      {"anonymous": False,
                       "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"},
                                  {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
                                  {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}],
                       "name": "Transfer", "type": "event"}, {"constant": True, "inputs": [], "name": "_decimals",
                                                              "outputs": [{"internalType": "uint8", "name": "",
                                                                           "type": "uint8"}], "payable": False,
                                                              "stateMutability": "view", "type": "function"},
                      {"constant": True, "inputs": [], "name": "_name",
                       "outputs": [{"internalType": "string", "name": "", "type": "string"}], "payable": False,
                       "stateMutability": "view", "type": "function"},
                      {"constant": True, "inputs": [], "name": "_symbol",
                       "outputs": [{"internalType": "string", "name": "", "type": "string"}], "payable": False,
                       "stateMutability": "view", "type": "function"}, {"constant": True, "inputs": [
                     {"internalType": "address", "name": "owner", "type": "address"},
                     {"internalType": "address", "name": "spender", "type": "address"}], "name": "allowance",
                                                                        "outputs": [
                                                                            {"internalType": "uint256", "name": "",
                                                                             "type": "uint256"}], "payable": False,
                                                                        "stateMutability": "view", "type": "function"},
                      {"constant": False, "inputs": [{"internalType": "address", "name": "spender", "type": "address"},
                                                     {"internalType": "uint256", "name": "amount", "type": "uint256"}],
                       "name": "approve", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                       "payable": False, "stateMutability": "nonpayable", "type": "function"},
                      {"constant": True, "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
                       "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                       "payable": False, "stateMutability": "view", "type": "function"},
                      {"constant": False, "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
                       "name": "burn", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                       "payable": False, "stateMutability": "nonpayable", "type": "function"},
                      {"constant": True, "inputs": [], "name": "decimals",
                       "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}], "payable": False,
                       "stateMutability": "view", "type": "function"}, {"constant": False, "inputs": [
                     {"internalType": "address", "name": "spender", "type": "address"},
                     {"internalType": "uint256", "name": "subtractedValue", "type": "uint256"}],
                                                                        "name": "decreaseAllowance", "outputs": [
                         {"internalType": "bool", "name": "", "type": "bool"}], "payable": False,
                                                                        "stateMutability": "nonpayable",
                                                                        "type": "function"},
                      {"constant": True, "inputs": [], "name": "getOwner",
                       "outputs": [{"internalType": "address", "name": "", "type": "address"}], "payable": False,
                       "stateMutability": "view", "type": "function"}, {"constant": False, "inputs": [
                     {"internalType": "address", "name": "spender", "type": "address"},
                     {"internalType": "uint256", "name": "addedValue", "type": "uint256"}], "name": "increaseAllowance",
                                                                        "outputs": [{"internalType": "bool", "name": "",
                                                                                     "type": "bool"}], "payable": False,
                                                                        "stateMutability": "nonpayable",
                                                                        "type": "function"},
                      {"constant": False, "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
                       "name": "mint", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                       "payable": False, "stateMutability": "nonpayable", "type": "function"},
                      {"constant": True, "inputs": [], "name": "name",
                       "outputs": [{"internalType": "string", "name": "", "type": "string"}], "payable": False,
                       "stateMutability": "view", "type": "function"}, {"constant": True, "inputs": [], "name": "owner",
                                                                        "outputs": [
                                                                            {"internalType": "address", "name": "",
                                                                             "type": "address"}], "payable": False,
                                                                        "stateMutability": "view", "type": "function"},
                      {"constant": False, "inputs": [], "name": "renounceOwnership", "outputs": [], "payable": False,
                       "stateMutability": "nonpayable", "type": "function"},
                      {"constant": True, "inputs": [], "name": "symbol",
                       "outputs": [{"internalType": "string", "name": "", "type": "string"}], "payable": False,
                       "stateMutability": "view", "type": "function"},
                      {"constant": True, "inputs": [], "name": "totalSupply",
                       "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "payable": False,
                       "stateMutability": "view", "type": "function"}, {"constant": False, "inputs": [
                     {"internalType": "address", "name": "recipient", "type": "address"},
                     {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "transfer", "outputs": [
                     {"internalType": "bool", "name": "", "type": "bool"}], "payable": False,
                                                                        "stateMutability": "nonpayable",
                                                                        "type": "function"}, {"constant": False,
                                                                                              "inputs": [{
                                                                                                             "internalType": "address",
                                                                                                             "name": "sender",
                                                                                                             "type": "address"},
                                                                                                         {
                                                                                                             "internalType": "address",
                                                                                                             "name": "recipient",
                                                                                                             "type": "address"},
                                                                                                         {
                                                                                                             "internalType": "uint256",
                                                                                                             "name": "amount",
                                                                                                             "type": "uint256"}],
                                                                                              "name": "transferFrom",
                                                                                              "outputs": [{
                                                                                                              "internalType": "bool",
                                                                                                              "name": "",
                                                                                                              "type": "bool"}],
                                                                                              "payable": False,
                                                                                              "stateMutability": "nonpayable",
                                                                                              "type": "function"},
                      {"constant": False,
                       "inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}],
                       "name": "transferOwnership", "outputs": [], "payable": False, "stateMutability": "nonpayable",
                       "type": "function"}],
             "cds": [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"anonymous": False,
                                                                                              "inputs": [
                                                                                                  {"indexed": True,
                                                                                                   "internalType": "address",
                                                                                                   "name": "owner",
                                                                                                   "type": "address"},
                                                                                                  {"indexed": True,
                                                                                                   "internalType": "address",
                                                                                                   "name": "spender",
                                                                                                   "type": "address"},
                                                                                                  {"indexed": False,
                                                                                                   "internalType": "uint256",
                                                                                                   "name": "value",
                                                                                                   "type": "uint256"}],
                                                                                              "name": "Approval",
                                                                                              "type": "event"},
                     {"anonymous": False, "inputs": [
                         {"indexed": True, "internalType": "address", "name": "previousOwner", "type": "address"},
                         {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}],
                      "name": "OwnershipTransferred", "type": "event"}, {"anonymous": False, "inputs": [
                     {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
                     {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
                     {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}],
                                                                         "name": "Transfer", "type": "event"},
                     {"inputs": [], "name": "_decimals",
                      "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}], "stateMutability": "view",
                      "type": "function"}, {"inputs": [], "name": "_name",
                                            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
                                            "stateMutability": "view", "type": "function"},
                     {"inputs": [], "name": "_symbol",
                      "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view",
                      "type": "function"}, {"inputs": [{"internalType": "address", "name": "owner", "type": "address"},
                                                       {"internalType": "address", "name": "spender",
                                                        "type": "address"}], "name": "allowance",
                                            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                                            "stateMutability": "view", "type": "function"}, {
                         "inputs": [{"internalType": "address", "name": "spender", "type": "address"},
                                    {"internalType": "uint256", "name": "amount", "type": "uint256"}],
                         "name": "approve", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                         "stateMutability": "nonpayable", "type": "function"},
                     {"inputs": [{"internalType": "address", "name": "account", "type": "address"}],
                      "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                      "stateMutability": "view", "type": "function"},
                     {"inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "burn",
                      "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {
                         "inputs": [{"internalType": "address", "name": "account", "type": "address"},
                                    {"internalType": "uint256", "name": "amount", "type": "uint256"}],
                         "name": "burnFrom", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
                     {"inputs": [], "name": "decimals",
                      "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}], "stateMutability": "view",
                      "type": "function"}, {
                         "inputs": [{"internalType": "address", "name": "spender", "type": "address"},
                                    {"internalType": "uint256", "name": "subtractedValue", "type": "uint256"}],
                         "name": "decreaseAllowance", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                         "stateMutability": "nonpayable", "type": "function"}, {"inputs": [], "name": "getOwner",
                                                                                "outputs": [{"internalType": "address",
                                                                                             "name": "",
                                                                                             "type": "address"}],
                                                                                "stateMutability": "view",
                                                                                "type": "function"}, {
                         "inputs": [{"internalType": "address", "name": "spender", "type": "address"},
                                    {"internalType": "uint256", "name": "addedValue", "type": "uint256"}],
                         "name": "increaseAllowance", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                         "stateMutability": "nonpayable", "type": "function"}, {"inputs": [], "name": "name",
                                                                                "outputs": [{"internalType": "string",
                                                                                             "name": "",
                                                                                             "type": "string"}],
                                                                                "stateMutability": "view",
                                                                                "type": "function"},
                     {"inputs": [], "name": "owner",
                      "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                      "stateMutability": "view", "type": "function"},
                     {"inputs": [], "name": "renounceOwnership", "outputs": [], "stateMutability": "nonpayable",
                      "type": "function"}, {"inputs": [], "name": "symbol",
                                            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
                                            "stateMutability": "view", "type": "function"},
                     {"inputs": [], "name": "totalSupply",
                      "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                      "stateMutability": "view", "type": "function"}, {
                         "inputs": [{"internalType": "address", "name": "recipient", "type": "address"},
                                    {"internalType": "uint256", "name": "amount", "type": "uint256"}],
                         "name": "transfer", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                         "stateMutability": "nonpayable", "type": "function"}, {
                         "inputs": [{"internalType": "address", "name": "sender", "type": "address"},
                                    {"internalType": "address", "name": "recipient", "type": "address"},
                                    {"internalType": "uint256", "name": "amount", "type": "uint256"}],
                         "name": "transferFrom", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                         "stateMutability": "nonpayable", "type": "function"},
                     {"inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}],
                      "name": "transferOwnership", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
             }

wallet_db = {"btc": "mainnet",
             "ltc": "mainnet",
             "doge": "mainnet",
             "eth": "mainnet",
             "usdc": "mainnet",
             "usdt": "mainnet",
             "shib": "mainnet",
             "pussy": "mainnet",
             "cds": "mainnet",
             "matic": "mainnet",
             "bnb": "mainnet",
             "busd": "mainnet",
             "op": "mainnet",
             "avax": "mainnet",
             "xrp": "mainnet",
             "xmr": "mainnet",
             "sol": "mainnet",
             "fluffy": "mainnet"
             }

sc_tokens = ["usdc", "usdt", "shib", "pussy", "busd", "cds"]

token_api_url = {
    "usdc": f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={contract_addy['usdt']}&apikey=JY8BVWUB1R54M382P2UA1EWGA8QT86UXJQ",
    "usdt": f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={contract_addy['usdc']}&apikey=JY8BVWUB1R54M382P2UA1EWGA8QT86UXJQ",
    "shib": f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={contract_addy['shib']}&apikey=JY8BVWUB1R54M382P2UA1EWGA8QT86UXJQ",
    "pussy": f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={contract_addy['pussy']}&apikey=JY8BVWUB1R54M382P2UA1EWGA8QT86UXJQ",
    "busd": f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={contract_addy['busd']}&apikey=6XE8C2KIIBQTJD7Q8G2M1RNF8UIKAI1RHU",
    "cds": f"https://api.bscscan.com/api?module=account&action=tokentx&contractaddress={contract_addy['cds']}&apikey=6XE8C2KIIBQTJD7Q8G2M1RNF8UIKAI1RHU"
    }

sol_token_api_url = {
    }




async def to_atomic(coin: str, amount: str) -> int:
    try:
        return int(Decimal(amount) / atomdic[coin.lower()])
    except:
        return 0


async def from_atomic(coin: str, amount: int) -> Decimal:
    try:
        return Decimal(atomdic[coin.lower()] * Decimal(amount))
    except:
        return Decimal(0)


def t_to_atomic(coin: str, amount: str) -> int:
    try:
        return int(Decimal(amount) / atomdic[coin.lower()])
    except:
        return 0


def t_from_atomic(coin: str, amount: int) -> Decimal:
    try:
        return Decimal(atomdic[coin.lower()] * Decimal(amount))
    except:
        return Decimal(0)


# Command List
cmd_list = [["help", 0], ["swaphelp", 0], ["escrowhelp", 0], ["stakehelp", 0], ["loanhelp", 0], ["bathelp", 0],
            ["fafhelp", 0],
            ["wallethelp", 0], ["profilehelp", 0], ["staffhelp", 1], ["hosthelp", 3],
            ["confighelp", 3]]
# Basic Commands
cmd_list += [["commands", 0], ["status", 0], ["time", 0], ["ping", 0], ["locale", 0], ["profile", 0], ["privacy", 0], ["rank", 0],
             ["ranks", 0], ["servers", 0], ["about", 0], ["version", 0], ["how2earn", 0], ["friend", 0], ["unfriend", 0], ["mail", 0],
             ["support", 0]]
# Wallet Commands
cmd_list += [["price", 0], ["convert", 0], ["coins", 0], ["rate", 0], ["tip", 0], ["send", 0], ["airdrop", 0],
             ["bal", 0], ["bals", 0], ["swapbal", 0], ["dep", 0], ["deposit", 0], ["withdraw", 0], ["escrow", 0], ["testswap", 0],
             ["swap", 0]]
# Advanced Commands
cmd_list += [["netlink", 0], ["whitelist", 0]
             ]
# Host Commands
cmd_list += [["config", 3], ["stafflist", 0], ["purge", 3], ["isnoreply", 3], ["setstaff", 3], ["removestaff", 3], ["noreply", 3]]
# Admin Commands
cmd_list += [["say", 9], ["setauth", 9], ["setlevel", 9], ["u_ban", 6], ["u_unban", 6],
             ["enable", 9], ["disable", 5], ["restart", 9], ["update_banlist", 9], ["credit", 9], ["mass_credit", 9], ["debit", 9], ["mass_debit", 9],
             ["dump", 9], ["webadmin2fa", 9], ["depcredit", 9], ["announce", 9]]
# Test Commands
cmd_list += [["authtest", 4], ["setbal", 9], ["discrepancy", 6], ["gmfc", 9], ["import_banlist", 9], ["check_bal", 6]]
cmd_strlist = [str(x[0]) for x in cmd_list]

# Auth Levels
# 0 - Regular user
# 1 - Host Server Mod
# 2 - Host Server Admin
# 3 - Host Server Owner
# 4 - UTTCex Staff Mod
# 5 - UTTCex Staff Admin
# 6 - UTTCex Staff Exchange Operator
# 7 - UTTCex Staff Developer
# 8 - UTTCex Staff Senior Developer
# 9 - Super Admin

# Static Embeds
e_basichelp = Embed(title="👋 Welcome to UTTCex!",
                            description="UTTCex is a powerful, all-in-one cryptocurrency bot!\n\nUTTCex is a tip bot, swap bot, staking bot, escrow bot, loan bot, and auto trade bot.\n\n**Note: __UTTCex does not accept `$tip` money from Tip.CC__! Don't $tip me**!\n\nUse `u.commands` for the command list to get started.\n\n**More help:**\n```\nu.swaphelp\nu.stakehelp\nu.escrowhelp\nu.loanhelp\nu.confighelp\nu.staffhelp\nu.ustaffhelp\nu.bathelp```",
                            color=0xffffff)
e_swaphelp = Embed(title="🔄 Swap Help",
                           description=f"Swapping cryptocurrencies on UTTCex is native and seamless.\nNo other bots are needed.\n\n**Note:** __Do not__ send money to UTTCex with <@{bot_ids[BOT_CFG_FLAG]['tipcc']}> via `$tip`!\nYou will lose your money!\n\n**To Get Started:" + "**\n`u.testswap` `{amount}` `{coin1}` `{coin2}`\n`u.swap` `{amount}` `{coin1}` `{coin2}`" + f"\n\nYou may also perform swaps in DM, away from prying eyes.",
                           color=0xffffff)
e_stakehelp = Embed(title="💎 Stake Help",
                    description=f"Staking cryptocurrency is also very easy with UTTCex.\n\n**Note:** __Do not__ send money to UTTCex with <@{bot_ids[BOT_CFG_FLAG]['tipcc']}> via `$tip`!\nYou will lose your money!\n\n**To Get Started:**\n" + "`u.stake` `{coin}` `{amount}`" + f"\n\nYou will be guided through the stake process.\n* You will be asked to confirm the stake 2 times.",
                    color=0xffffff)
e_escrowhelp = Embed(title="👨‍🔧 Escrow Help",
                             description=f"Escrow cryptocurrencies with UTTCex to safely trade with unknown users of any amount!\nEscrow is a **__free__** service and always will be.\nUse `u.escrow` `@user` to begin an escrow.\n\nYou may not engage in more than one escrow session at a time.\n\nBoth parties will be immediately locked into escrow.\n\nIf you are locked in escrow by accident, simply use `u.escrow cancel` in case someone accidentally @ mentioned you.\n\nUse `u.escrow` with no parameters for more detailed help.",
                             color=0xffffff)
e_autotrade_help = Embed(title="🔄 Blind Auto-Trade Help",
                                 description="**BAT** or \"**Fire & Forget**\" trading is perfect for those who don't want to spend the time, or don't have the time to spend trading crypto for hours a day.\n\nThis service helps you trade your crypto for the coins you want at the rates you want. A trade does not complete unless your conditions are satisfied.\n\nIf there are any unsatisfied conditions, they will idle in the auto trade pool until completed or cancelled by you.\n\nThe pool and listings cannot be viewed to prevent trade offer targeting or artificial price gap creation.",
                                 color=0xffffff)
e_config_help = Embed(title="Configuration Help",
                              description="Usage:\n```u.config set {flag} {ID}```\nAvailable flags:\n> **TC** - Trade Channel\n> **LC** - Profit Logs Channel\n> **AC** - Airdrop Channel\n> **TLC** - Tip Log Channel\n\n**Adding and Removing Staff:**\n```u.setstaff {ID} {type}```\nAvailable types:\n> **mod** / **moderator**\n> **admin** / **administrator**",
                              color=0xffffff)

# Special String Constants
rchars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_=:."

# Log for GUI Message Stack
gui_log1 = [0]
gui_log2 = [1]

# Malicious Server List
malicious_server_list = [1062756013142450286]

# Admin List
admin_list = [893678556352237639, 1057133315527815209, 1102858475329048676]
tester_list = [893678556352237639, 547924592715366405, 263840616499118082, 514580452187832324, 271325189373952010]
admin_only = False
tester_only = True

authorized_bots = [bot_ids[BOT_CFG_FLAG]["rabbitswap"]]

# Timestamp
async def timestamp() -> str:
    return f"{datetime.datetime.now().strftime('%H:%M:%S')} {datetime.date.fromtimestamp(time.time())}"

async def timedstamp(t) -> str:
    dt = datetime.datetime.fromtimestamp(t)
    return f"{dt.strftime('%H:%M:%S')} {dt.date()}"


# Date from time.time()
#async def date(time: float) -> str:
#    return str(datetime.date.fromtimestamp(time))


def main():
    client.run(bot_tokens[BOT_CFG_FLAG]["token"], reconnect=True)
    return


scheduled_messages = []


@client.event
async def on_ready():
    await gprint(f"Under The Table Coin Centralized Exchange v5 Ready", "topright", "log")
    act = discord.Activity(name=f"your favor.", type=5)
    await client.change_presence(status=discord.Status.online, activity=act)
    #
    # Start our threads here
    #
    # Coin deposit detection threads
    deposit_monitor_thread = newthread(target=deposit_monitor_client_thread)
    wallet_threads = [#newthread(target=wallet_utxo_update_thread, args=("sol",)),
                      #newthread(target=wallet_utxo_update_thread, args=("xrp",))
                      # newthread(target = wallet_utxo_update_thread, args = ("uttc",)),
                      # newthread(target = wallet_utxo_update_thread, args = ("xmr",))
                      ]

    deposit_monitor_thread.start()

    # Exchange stats update thread (Discord Voice Channel Names)
    ex_stats_update_thread = newthread(target=exchange_stats_update_thread, args=())
    ex_stats_update_thread.start()  # Start the thread

    # Price check update thread!
    price_check_thread = newthread(target=price_update_thread, args=())
    price_check_thread.start()

    # Super GUI Threads
    gui_thread1 = newthread(target=uttcex_gui, args=(gui_log1,))
    gui_thread2 = newthread(target=uttcex_gui, args=(gui_log2,))
    gui_thread1.start()
    gui_thread2.start()

    # Database Backup Manager!
    db_backup_thread = newthread(target=database_backup_manager)
    db_backup_thread.start()

    #for t in wallet_threads:
        #t.start()
    return


last_mq_reply = time.time()

net_chat_bot_ids = [1153487638624489549, 1153486971231027255, 1140656764967194644, 1155413393184919582,
                    1155708160720511087, 1155413393184919582, 1153184201236041798]
tipbot_ids = [617037497574359050, 474841349968101386]
swapbot_ids = [918146218511708260, 1007383181403639928]

no_bot_list = net_chat_bot_ids + tipbot_ids + swapbot_ids


async def get_lang(target: str) -> str:
    return profile_locale[(await sql_select("uttcex_bot_db", "profiles", "discord_id", target))[2]]

whitelist = {0: [824259447412359168, 1051896202192502844, 888343445465354250, 1183051591763374140, 992999354241663017, 898823445217947659, 842893810018942997, 828672809110077441,
             795349722545258516, 1212281132163407892, 1214681119002468402, 897546129108008960, 843653317313691648, 1138847688620777502, 1161639586431242274, 503152242409340930,
                 991654257935798273, 1251220238624620695],
             -1: [824259447412359168, 1051896202192502844]
             }

bot_whitelist = {0: [],
                 -1: []
                 }

known_words = [x[0] for x in cmd_list if x[1] <= 2]

def get_closest_match(input_word, known_words):
    closest_match = process.extractOne(input_word, known_words)
    return closest_match[0] if closest_match else None

@client.event
async def on_message(msg: discord.Message):
    global scheduled_messages
    if shutdown == True:
        await client.close()
        exit()

    if msg.guild is None:
        pass
    elif msg.guild.id not in whitelist[BOT_CFG_FLAG]:
        return
        
    lock = threading.Lock()        

    if (await has_profile(msg.author.id)) == True: # has_profile() creates one if nonexistent
        pass

    # Log that shit
    display_bot_messages = True
    if (msg.content == ""):  # Embedded shit, reject
        pass
    else:
        if (msg.author.bot == True):
            if (msg.author.id in net_chat_bot_ids):  # Network Chat bot messages in a separate window
                await gprint(
                    f"[INFO] New Message ===========================\n[INFO] Origin Server: {msg.guild.name}\n[INFO] Sender: {msg.author.name} :: {msg.author.id}\n[INFO] Channel ID: {msg.channel.id}\n[INFO] Bot: TRUE\n[INFO] Timestamp: {await timestamp()}\n[INFO] Message:\n==============================================\n{msg.content}\n==============================================\n",
                    "botleft", "chat")
                return  # We can return from network chat. We do not want to process anything from here.
            elif (msg.author.id in tipbot_ids):  # Tip bot messages in a separate window
                await gprint(
                    f"[INFO] New Message ===========================\n[INFO] Origin Server: {msg.guild.name}\n[INFO] Sender: {msg.author.name} :: {msg.author.id}\n[INFO] Channel ID: {msg.channel.id}\n[INFO] Bot: TRUE\n[INFO] Timestamp: {await timestamp()}\n[INFO] Message:\n==============================================\n{msg.content}\n==============================================\n",
                    "topright", "chat")
                try:
                    await gprint(
                        f"[INFO] New Message ===========================\n[INFO] Origin Server: {msg.guild.name}\n[INFO] Sender: {msg.author.name} :: {msg.author.id}\n[INFO] Channel ID: {msg.channel.id}\n[INFO] Bot: TRUE\n[INFO] Timestamp: {await timestamp()}\n[INFO] Message:\n==============================================\n{msg.content}\n==============================================\n",
                        "topright", "chat")
                except:
                    await gprint(
                        f"[INFO] New Message ===========================\n[INFO] Sender: {msg.author.name} :: {msg.author.id}\n[INFO] Sender: {msg.author.name} :: {msg.author.id}\n[INFO] Channel ID: {msg.channel.id}\n[INFO] Bot: TRUE\n[INFO] Timestamp: {await timestamp()}\n[INFO] Message:\n==============================================\n{msg.content}\n==============================================\n",
                        "topright", "chat")
            elif (msg.author.id in swapbot_ids):  # Swap bot messages in a separate window
                await gprint(
                    f"[INFO] New Message ===========================\n[INFO] Origin Server: {msg.guild.name}\n[INFO] Sender: {msg.author.name} :: {msg.author.id}\n[INFO] Channel ID: {msg.channel.id}\n[INFO] Bot: TRUE\n[INFO] Timestamp: {await timestamp()}\n[INFO] Message:\n==============================================\n{msg.content}\n==============================================\n",
                    "botright", "chat")
                try:
                    await gprint(
                        f"[INFO] New Message ===========================\n[INFO] Origin Server: {msg.guild.name}\n[INFO] Sender: {msg.author.name} :: {msg.author.id}\n[INFO] Channel ID: {msg.channel.id}\n[INFO] Bot: TRUE\n[INFO] Timestamp: {await timestamp()}\n[INFO] Message:\n==============================================\n{msg.content}\n==============================================\n",
                        "botright", "chat")
                except:
                    await gprint(
                        f"[INFO] New Message ===========================\n[INFO] Sender: {msg.author.name} :: {msg.author.id}\n[INFO] Sender: {msg.author.name} :: {msg.author.id}\n[INFO] Channel ID: {msg.channel.id}\n[INFO] Bot: TRUE\n[INFO] Timestamp: {await timestamp()}\n[INFO] Message:\n==============================================\n{msg.content}\n==============================================\n",
                        "botright", "chat")
        elif (msg.author.bot == False):
            try:
                await gprint(
                    f"[INFO] New Message ===========================\n[INFO] Origin Server: {msg.guild.name}\n[INFO] Sender: {msg.author.name} :: {msg.author.id}\n[INFO] Channel ID: {msg.channel.id}\n[INFO] Timestamp: {await timestamp()}\n[INFO] Message:\n==============================================\n{msg.content}\n==============================================\n",
                    "topleft", "chat")
            except:
                await gprint(
                    f"[INFO] New Message ===========================\n[INFO] Origin: Direct Message\n[INFO] Sender: {msg.author.name} :: {msg.author.id}\n[INFO] Channel ID: {msg.channel.id}\n[INFO] Timestamp: {await timestamp()}\n[INFO] Message:\n==============================================\n{msg.content}\n==============================================\n",
                    "topleft", "chat")

    # Network Chat Webhook
    if (msg.content.startswith("=====")):
        mx = (msg.content.replace("=====\n**", ""))[msg.content.find("**"):].replace("**\n", "")
        mx = await sanistr(mx[2:len(msg)]).lower()
        ch = client.get_channel(1152199028730236958)
        await ch.send(mx)
    elif (msg.content.startswith("*****")):  # It's Father Crypto
        ch = client.get_channel(1152199028730236958)
        mx = msg.content
        await ch.send(mx)

    ####
    # Deposit detection
    ####

    lang = profile_locale["0"]
    try:
        lang = profile_locale[
            (await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(msg.author.id)))[2]]
    except:
        pass

    if len(scheduled_messages) > 0:
        print(f"SCHEDULE: {scheduled_messages}\n")
        mx = None
        for message in scheduled_messages:
            print(f"MESSAGE: {message}\n")
            mx = message
            if len(message) == 5:
                # Check if DM was already sent by checking "credited" value with txid and coin
                user = message[0]
                coin = message[1]
                table = f"{coin}_utxos"
                amount = int(message[2])
                txid = message[3]
                uttcex_id = message[4]
                data = await sql_select(wallet_db[coin], table,"*", "*")
                data = [x for x in data if x[0] == txid and x[3] != "1"]
                data = data[0]
                if coin == "fluffy": # SOL TOKEN SPECIAL CATCH
                    table = "sol_utxos"
                    address = await udefs.udefs.get_sol_address_from_uid(uttcex_id)
                    data = await sql_select(wallet_db[coin], table, "*", "*")
                    data = [x for x in data if x[5] == txid and x[3] == "0"]
                    data = data[0]
                    credited = data[3]
                else:
                    address = await udefs.udefs.get_address_from_uid(uttcex_id, coin)
                    data = await sql_select(wallet_db[coin], table, "*", "*")
                    data = [x for x in data if x[0] == txid and x[3] == "0"]
                    data = data[0]
                    credited = data[3]
                lang = profile_locale[
                    (await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(user)))[2]]
                amount = await from_atomic(coin, amount)
                if (credited == "0"):
                    # Credit, and set appropriately.
                    t_gprint(
                        f"\n[INFO] ======================= {coin.upper()} =======================\n[INFO] Timestamp: {await timestamp()}\n[INFO] Coin: {coin}\n[INFO] Amount: {amount}\n[INFO] TX Hash: {txid}\n[INFO] ================================================\n",
                        "topleft", "log")
                    await swap_credit(user, coin, amount)
                    if (coin == "fluffy"):
                        wdb = wallet_db["sol"]
                        await sql_do(wdb, f"UPDATE `{table}` SET `credited` = '1', `io_flag` = '1' WHERE `fluffy_tx_hash` = '{txid}' AND `credited` = '0' AND `receiving_address` = '{address}'")
                    else:
                        await sql_do(wallet_db[coin], f"UPDATE `{table}` SET `credited` = '1', `io_flag` = '1' WHERE `tx_hash` = '{txid}' AND `credited` = '0' AND `receiving_address` = '{address}'")
                    e = discord.Embed(
                        title= f"{emojis[coin]} {locale_msg[lang]['dm_deposit_title_1']} {coin.upper()} {locale_msg[lang]['dm_deposit_title_2']}",
                        description=f"** {amount} {emojis[coin]}**\n\n**Transaction Hash (ID):**\n```\n{txid}\n```",
                        color=0x00ff00)
                    try:
                        await edm(user, e)
                        print("- DEPOSIT NOTIFICATION SENT TO USER -")
                    except:
                        pass  # UTTCex received this shit
                    e = discord.Embed(title=f"{emojis[coin]} Internal Deposit Log",
                                      description=f"**Timestamp:**\n`{await timestamp()}`\n\n**Coin:**\n`{coin}`\n\n**Amount:**\n`{amount}`\n\n**TX Hash:**\n`{txid}`",
                                      color=0x00ff00)
                    ch = client.get_channel(deposit_log_channel)
                    await ch.send(embed=e)
                    break
            if len(message) == 3:
                ch = client.get_channel(int(message[0]))
                x = message[1]
                flag = bool(message[2])
                if flag is True: # Embed
                    await ch.send(embed = x)
                elif flag is False: # Regular message
                    await ch.send(x)
                break
        try:
            scheduled_messages.remove(mx)
        except:
            pass

    ####
    # Chat Level & Experience Trigger
    ####

    ####
    # Command Handler from DM
    ####
    if not msg.guild:
        if (msg.content.lower().startswith("u.")):
            if (await has_profile(msg.author.id) == True):
                if ((await is_banned(msg.author.id)) == True):
                    data = await sql_select("uttcex_bot_db", "profiles", "discord_id", str(msg.author.id))
                    reason = data[21]
                    additional = data[25]
                    if additional == "":
                        additional = "None."
                    e = discord.Embed(title="❌ YOU ARE BANNED ❌",
                                      description=f"<@{str(msg.author.id)}>\n\nThis Discord account was permanently banned for:\n```ansi\n\u001b[0;40;31m{reason}\u001b[0;0m```",
                                      color=0xff0000)
                    e.set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/987754157756780574/1162250849704230922/403_avatar.gif")
                    e.add_field(name="Additional Information", value=f"{additional}", inline=False)
                    e.set_footer(
                        text="Do not interact with this user for any reason.\nThis user cannot send or receive tips, or use UTTCex at all.")
                    await ereply(msg, e)
                    return
            tmp = list(msg.content[2:].split(" "))[0].lower()
            if (await is_cmd(tmp) == True):
                if (await has_auth(msg) == True):
                    if ((admin_only == True) and (tester_only == False)):
                        if ((msg.author.id not in admin_list) or (msg.author.id not in tester_list)):
                            e = discord.Embed(title="Admin Only",
                                              description="### UTTCex is in Admin-Only mode currently for testing.\nPlease try later.",
                                              color=0xffffff)
                            await ereply(msg, e)
                            return
                    elif ((admin_only == True) and (tester_only == True)):
                        if ((msg.author.id not in admin_list) or (msg.author.id not in tester_list)):
                            e = discord.Embed(title="Admin Only",
                                              description="### UTTCex is in Admin-Only mode currently for testing.\nPlease try later.",
                                              color=0xffffff)
                            await ereply(msg, e)
                            return
                    await do_cmd(tmp, msg)
                    return
                await err(1, [msg, msg.content])
                return
            rec_cmd = get_closest_match(tmp, known_words)
            await err(0, [msg, f"u.{rec_cmd} is valid.\nu.{tmp}"])
            return
    # Command Handler for UTTCex
    if (msg.author.id == bot_ids[BOT_CFG_FLAG]["uttcex"]):
        if ((await sanistr(msg.content)).lower().startswith("u.")):
            if (await is_banned(msg.author.id) == True):
                await err(-3, [msg])
                return
            tmp = list((await sanistr(msg.content))[2:].split(" "))[0]
            if (await is_cmd(tmp) == True):
                await do_cmd(tmp, msg)
                return
        return
    # Command Handler for Users
    if ((await sanistr(msg.content)).lower().startswith("u.")):
        if (await is_banned(msg.author.id) == True):
            if (await has_profile(msg.author.id) == True):
                if ((await is_banned(msg.author.id)) == True):
                    data = await sql_select("uttcex_bot_db", "profiles", "discord_id", str(msg.author.id))
                    reason = data[21]
                    additional = data[25]
                    if additional == "":
                        additional = "None."
                    e = discord.Embed(title="❌ YOU ARE BANNED ❌",
                                      description=f"<@{str(msg.author.id)}>\n\nThis Discord account was permanently banned for:\n```ansi\n\u001b[0;40;31m{reason}\u001b[0;0m```",
                                      color=0xff0000)
                    e.set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/987754157756780574/1162250849704230922/403_avatar.gif")
                    e.add_field(name="Additional Information", value=f"{additional}", inline=False)
                    e.set_footer(
                        text="Do not interact with this user for any reason.\nThis user cannot send or receive tips, or use UTTCex at all.")
                    await ereply(msg, e)
                    return
        tmp = list((await sanistr(msg.content))[2:].split(" "))[0]
        if (await is_cmd(tmp) == True):
            if (await has_auth(msg) == True):
                if ((admin_only == True) and (tester_only == False)):
                    if ((msg.author.id not in admin_list) or (msg.author.id not in tester_list)):
                        e = discord.Embed(title="Admin Only",
                                          description="### UTTCex is in Admin-Only mode currently for testing.\nPlease try later.",
                                          color=0xffffff)
                        await ereply(msg, e)
                        return
                elif ((admin_only == True) and (tester_only == True)):
                    if ((msg.author.id not in admin_list) or (msg.author.id not in tester_list)):
                        e = discord.Embed(title="Admin Only",
                                          description="### UTTCex is in Admin-Only mode currently for testing.\nPlease try later.",
                                          color=0xffffff)
                        await ereply(msg, e)
                        return
                nrcl = await sql_select("uttcex_bot_db", "no_reply", "channel_id", f"{msg.channel.id}")
                if nrcl is not None: # Entry exists  # -- REFACTOR THIS TO A FUNCTION, USED 3x HERE
                    if nrcl[1] == "1" and tmp.startswith("noreply") is False and tmp != "isnoreply":
                        return
                else:
                    pass
                await do_cmd(tmp, msg)
                return
            nrcl = await sql_select("uttcex_bot_db", "no_reply", "channel_id", f"{msg.channel.id}")
            if nrcl is not None: # Entry exists
                if nrcl[1] == "1" and tmp.startswith("noreply") is False and tmp != "isnoreply":
                    return
            else:
                pass
            await err(1, [msg, msg.content])
            return
        nrcl = await sql_select("uttcex_bot_db", "no_reply", "channel_id", f"{msg.channel.id}")
        if nrcl is not None: # Entry exists
            if nrcl[1] == "1" and tmp.startswith("noreply") is False and tmp != "isnoreply":
                return
        else:
            pass
        rec_cmd = get_closest_match(tmp, known_words)
        await err(0, [msg, f"u.{rec_cmd} is valid.\nu.{tmp}"])
        return

    async def refresh_airdrops():
        drops = t_sql_select("uttcex_bot_db", "airdrops", "*", "*")
        print("Refreshed airdrop list.")
        for drop in drops:
            current_time = Decimal(time.time())
            end_time = Decimal(drop[5])
            if current_time > end_time: # Complete the drop
                # Function call to code factored from on_react/on_raw_react ()'s
                start_time = Decimal(drop[4])
                mxchid = int(drop[7])
                mxid = int(drop[8])
                ch = client.get_channel(mxchid)
                mx = await ch.fetch_message(mxid)
                mxrid = int(drop[6])
                dropper = int(drop[0])
                coin = drop[1]
                amount = Decimal(drop[2])
                drop_id = drop[3]
                xparticipants = t_sql_select("uttcex_bot_db", "airdrops_participants", "*", "*")
                participants = []
                for x in xparticipants:
                    if x[0] == drop_id and int(x[1]) not in participants:
                        participants.append(int(x[1]))
                total = len(participants)
                if total == 0:
                    await backend_credit(int(dropper), amount, coin)
                    await raw_unlock_bal(int(dropper), coin, amount)
                    await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops` WHERE `drop_id` = '{drop_id}'")
                    e = mx.embeds[0]
                    e.description = f"Done, no users joined. Returned {format(amount, decidic[coin])} {emojis[coin]} to <@{dropper}>"
                    await mx.edit(embed = e)
                    return
                give = amount / total
                given = Decimal("0.0")
                places = len(format(atomdic[coin], decidic[coin]).replace("0.","").replace("f",""))
                round_factor = Decimal("1." + ("0" * places))
                give = give.quantize(round_factor, rounding=decimal.ROUND_DOWN)
                # Debit author, delete lock (even out), delete airdrop with drop ID, delete participant list with drop ID
                # Credit each user
                to_give = []
                index = 0
                while given + give <= Decimal(amount):
                    xuser = participants[index % total]
                    given += give
                    to_give.append([xuser, format(give, decidic[coin]), coin])
                    index += 1
                remainder = Decimal(amount) - given
                if remainder > 0:
                    xuser = participants[index % total]
                    to_give.append([xuser, format(remainder, decidic[coin]), coin])
                if (await raw_unlock_bal(dropper, coin, amount)) is False:
                    await mx.edit("Airdrop failed, an unknown error occurred.\n\nSupport has been notified.")
                    await support(mxr)
                    return
                else:
                    await backend_debit(dropper, amount, coin)
                    await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops` WHERE `drop_id` = '{drop_id}'")
                    await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops_participants` WHERE `drop_id` = '{drop_id}'")
                    for entry in to_give:
                        await backend_log_tip(dropper, entry[0], entry[1], coin) 
                        await backend_credit(entry[0], Decimal(entry[1]), coin)
                    e = mx.embeds[0]
                    recipients = [f"<@{x[0]}>" for x in to_give]
                    val = await get_price(coin)
                    val = format(val * give, ',.12f')
                    e.description = f"Done, {total} participants.\n\n{', '.join(recipients)}\n\nEach received **${val} USD**"
                    await mx.edit(embed = e)
                    return
            else:
                print(f"Drop {drop[3]} still running ..")
        print("Parsed airdrops.")
    await refresh_airdrops()
    return


# Member Joined Server
@client.event
async def on_member_join(m):
    # Primary UTTCex Server AKA Under The Table Network
    if (m.guild.id == 824259447412359168):
        ch = client.get_channel(909240601231388702)
        await ch.send(f"A new user has sat at the table. Welcome <@{m.user_id}>!")
        return


# Cached
@client.event
async def on_reaction_add(reaction, user):
    print("not raw add")
    mx = reaction.message             # Reacted message
    mxid = mx.id                      # Reacted message ID 
    mxchid = mx.channel.id            # Reacted message channel ID
    mxr = mx.reference                # Reacted message replied to this
    try:
        mxrid = mx.reference.message_id   # Replied to message ID
    except:
        return
    ch = client.get_channel(mxchid)
    mxr = await ch.fetch_message(mxrid)
    origin_author = mxr.author
    # Don't add UTTCex to the list or is the author
    if (int(user.id) == bot_ids[BOT_CFG_FLAG]["uttcex"]) or (int(user.id) == origin_author.id) or (await is_banned(user.id)) is True:
        if user.id not in admin_list or int(user.id) == bot_ids[BOT_CFG_FLAG]["uttcex"]:
            return
    # Get this airdrop's ID from the replied message ID of user message that sent u.airdrop x y z
    data = await sql_select("uttcex_bot_db", "airdrops", "message_id", str(mxrid))
    if data is None:
        return
    dropper = int(data[0]) # Dropper user ID
    coin = data[1]
    if (reaction.emoji.id != emojid[coin]):
        return
    amount = Decimal(data[2])
    drop_id = data[3]
    current_participants = await sql_select("uttcex_bot_db", "airdrops_participants", "*", "*")
    count = 0
    scanned = []
    if current_participants is None:
        current_participants = 0
    else:
        for x in current_participants:
            if x != [] and x != None and x[1] not in scanned:
                count += 1
                scanned.append(x[1])
        current_participants = count
    start_time = Decimal(data[4])
    end_time = Decimal(data[5])
    max_participants = await to_atomic(coin, amount) # If BTC, 0.00000003 = 3 participants
    current_time = time.time()
    if Decimal(current_time) < end_time:
        if current_participants < max_participants:  # less than, because each call adds a participant - less than or equal to would add 1 more than the max
            if current_participants + 1 == max_participants: # if this would be the last one, we finish the drop after adding the participant and concluding
                data = await sql_select("uttcex_bot_db", "airdrops_participants", "*", "*")
                if data is not None: # Data, check if joined
                    for x in data:
                        if x[1] == str(user.id) and x[0] == drop_id:
                            continue
                        await sql_do("uttcex_bot_db", f"INSERT INTO `airdrops_participants`(`drop_id`, `participant_id`) VALUES ('{drop_id}','{user.id}')")
                        break
                elif data is not None:
                    await sql_do("uttcex_bot_db", f"INSERT INTO `airdrops_participants`(`drop_id`, `participant_id`) VALUES ('{drop_id}','{user.id}')")
                # Don't return here so we can finalize
            else: # add participant and return
                data = await sql_select("uttcex_bot_db", "airdrops_participants", "*", "*")
                if data is not None: # Data, check if joined
                    for x in data:
                        if x[1] != str(user.id) and x[0] == drop_id:
                            continue
                        await sql_do("uttcex_bot_db", f"INSERT INTO `airdrops_participants`(`drop_id`, `participant_id`) VALUES ('{drop_id}','{user.id}')")
                        break
                elif data is None: # No data, insert
                    await sql_do("uttcex_bot_db", f"INSERT INTO `airdrops_participants`(`drop_id`, `participant_id`) VALUES ('{drop_id}','{user.id}')")
                # Don't return to check finalize
    # Finalize drop
    xparticipants = await sql_select("uttcex_bot_db", "airdrops_participants", "*", "*")
    if xparticipants is None:
        # Return money to dropper
        # Delete airdrop from `airdrops`
        await backend_credit(int(dropper), amount, coin)
        await raw_unlock_bal(int(dropper), coin, amount)
        await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops` WHERE `drop_id` = '{drop_id}'")
        e = mx.embeds[0]
        e.description = f"Done, no users joined. Returned {format(amount, decidic[coin])} {emojis[coin]} to <@{data[0]}>"
        await mx.edit(embed = e)
        return
    participants = []
    for x in xparticipants:
        if x[0] == drop_id and int(x[1]) not in participants:
            participants.append(int(x[1]))
    total = len(participants)
    if total == 0 and Decimal(current_time) > Decimal(end_time):
        # Return money to dropper
        # Delete airdrop from `airdrops`
        await backend_credit(int(dropper), amount, coin)
        await raw_unlock_bal(int(dropper), coin, amount)
        await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops` WHERE `drop_id` = '{drop_id}'")
        e = mx.embeds[0]
        e.description = f"Done, no users joined. Returned {format(amount, decidic[coin])} {emojis[coin]} to <@{data[0]}>"
        await mx.edit(embed = e)
        return
    elif total == max_participants and Decimal(current_time) <= Decimal(end_time):
        give = amount / total
        given = Decimal("0.0")
        places = len(format(atomdic[coin], decidic[coin]).replace("0.","").replace("f",""))
        round_factor = Decimal("1." + ("0" * places))
        give = give.quantize(round_factor, rounding=decimal.ROUND_DOWN)
        # Debit author, delete lock (even out), delete airdrop with drop ID, delete participant list with drop ID
        # Credit each user
        to_give = []
        index = 0
        while given + give <= Decimal(amount):
            xuser = participants[index % total]
            given += give
            to_give.append([xuser, format(give, decidic[coin]), coin])
            index += 1
        remainder = Decimal(amount) - given
        if remainder > 0:
            xuser = participants[index % total]
            to_give.append([xuser, format(remainder, decidic[coin]), coin])
        if (await raw_unlock_bal(dropper, coin, amount)) is False:
            await mx.edit("Airdrop failed, an unknown error occurred.\n\nSupport has been notified.")
            await support(mxr)
            return
        else:
            await backend_debit(dropper, amount, coin)
            await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops` WHERE `drop_id` = '{drop_id}'")
            await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops_participants` WHERE `drop_id` = '{drop_id}'")
            for entry in to_give:
                await backend_log_tip(dropper, entry[0], entry[1], coin) 
                await backend_credit(entry[0], Decimal(entry[1]), coin)
            e = mx.embeds[0]
            recipients = [f"<@{x[0]}>" for x in to_give]
            val = await get_price(coin)
            val = format(val * give, ',.12f')
            e.description = f"Done, {total} participants.\n\n{', '.join(recipients)}\n\nEach received **${val} USD**"
            await mx.edit(embed = e)
            return
    elif (total <= max_participants) and (total > 0) and (Decimal(current_time) > Decimal(end_time)):
        give = amount / total
        given = Decimal("0.0")
        places = len(format(atomdic[coin], decidic[coin]).replace("0.","").replace("f",""))
        round_factor = Decimal("1." + ("0" * places))
        give = give.quantize(round_factor, rounding=decimal.ROUND_DOWN)
        # Debit author, delete lock (even out), delete airdrop with drop ID, delete participant list with drop ID
        # Credit each user
        to_give = []
        index = 0
        while given + give <= Decimal(amount):
            xuser = participants[index % total]
            given += give
            to_give.append([xuser, format(give, decidic[coin]), coin])
            index += 1
        remainder = Decimal(amount) - given
        if remainder > 0:
            xuser = participants[index % total]
            to_give.append([xuser, format(remainder, decidic[coin]), coin])
        if (await raw_unlock_bal(dropper, coin, amount)) is False:
            await mx.edit("Airdrop failed, an unknown error occurred.\n\nSupport has been notified.")
            await support(mxr)
            return
        else:
            await backend_debit(dropper, amount, coin)
            await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops` WHERE `drop_id` = '{drop_id}'")
            await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops_participants` WHERE `drop_id` = '{drop_id}'")
            for entry in to_give:
                await backend_log_tip(dropper, entry[0], entry[1], coin) 
                await backend_credit(entry[0], Decimal(entry[1]), coin)
            e = mx.embeds[0]
            recipients = [f"<@{x[0]}>" for x in to_give]
            val = await get_price(coin)
            val = format(val * give, ',.12f')
            e.description = f"Done, {total} participants.\n\n{', '.join(recipients)}\n\nEach received **${val} USD**"
            await mx.edit(embed = e)
            return

# Cached
@client.event
async def on_reaction_remove(reaction, user):
    print("not raw remove")
    mx = reaction.message             # Reacted message
    mxid = mx.id                      # Reacted message ID 
    mxchid = mx.channel.id            # Reacted message channel ID
    mxr = mx.reference                # Reacted message replied to this
    try:
        mxrid = mx.reference.message_id   # Replied to message ID
    except:
        return
    ch = client.get_channel(mxchid)
    mxr = await ch.fetch_message(mxrid)
    origin_author = mxr.author
    if (int(user.id) == bot_ids[BOT_CFG_FLAG]["uttcex"]):
        return
    data = await sql_select("uttcex_bot_db", "airdrops", "*", "*")
    if data is not None:
        for drop in data:
            if Decimal(time.time()) > Decimal(drop[5]):
                return
            if int(drop[6]) == mxrid:
                if (reaction.emoji.id == emojid[drop[1]]):
                    return


# Not cached
@client.event
async def on_raw_reaction_add(reaction):
    print("raw add")
    mxid = reaction.message_id        # Reacted message ID
    mxchid = reaction.channel_id      # Reacted message channel ID
    ch = client.get_channel(mxchid)   # Channel of reacted message
    mx = await ch.fetch_message(mxid) # Reacted message
    mxr = mx.reference                # Reacted message replied to this
    try:
        mxrid = mx.reference.message_id   # Replied to message ID
    except:
        return
    mxr = await ch.fetch_message(mxrid)
    origin_author = mxr.author
    # Don't add UTTCex to the list or is the author
    if (int(reaction.user_id) == bot_ids[BOT_CFG_FLAG]["uttcex"]) or (int(reaction.user_id) == origin_author.id) or (await is_banned(reaction.user_id)) is True:
        if reaction.user_id not in admin_list or int(reaction.user_id) == bot_ids[BOT_CFG_FLAG]["uttcex"]:
            return
    # Get this airdrop's ID from the replied message ID of user message that sent u.airdrop x y z
    data = await sql_select("uttcex_bot_db", "airdrops", "message_id", str(mxrid))
    if data is None: # Airdrop doesn't exist anymore
        return       # Airdrop doesn't exist anymore
    dropper = int(data[0]) # Dropper user ID
    coin = data[1]
    if (reaction.emoji.id != emojid[coin]):
        return
    amount = Decimal(data[2])
    drop_id = data[3]
    current_participants = await sql_select("uttcex_bot_db", "airdrops_participants", "*", "*")
    count = 0
    scanned = []
    if current_participants is None:
        current_participants = 0
    else:
        for x in current_participants:
            if x != [] and x != None and x[1] not in scanned:
                count += 1
                scanned.append(x[1])
        current_participants = count
    start_time = Decimal(data[4])
    end_time = Decimal(data[5])
    max_participants = await to_atomic(coin, amount) # If BTC, 0.00000003 = 3 participants
    current_time = time.time()
    if Decimal(current_time) < end_time:
        if current_participants < max_participants:  # less than, because each call adds a participant - less than or equal to would add 1 more than the max
            if current_participants + 1 == max_participants: # if this would be the last one, we finish the drop after adding the participant and concluding
                data = await sql_select("uttcex_bot_db", "airdrops_participants", "*", "*")
                if data is not None: # Data, check if joined
                    for x in data:
                        if x[1] == str(reaction.user_id) and x[0] == drop_id:
                            continue
                        await sql_do("uttcex_bot_db", f"INSERT INTO `airdrops_participants`(`drop_id`, `participant_id`) VALUES ('{drop_id}','{reaction.user_id}')")
                        break
                elif data is None: # No data, insert
                    await sql_do("uttcex_bot_db", f"INSERT INTO `airdrops_participants`(`drop_id`, `participant_id`) VALUES ('{drop_id}','{reaction.user_id}')")
                # Don't return here so we can finalize
            else: # add participant and return
                data = await sql_select("uttcex_bot_db", "airdrops_participants", "*", "*")
                if data is not None: # Data, check if joined
                    for x in data:
                        if x[1] == str(reaction.user_id) and x[0] == drop_id:
                            continue
                        await sql_do("uttcex_bot_db", f"INSERT INTO `airdrops_participants`(`drop_id`, `participant_id`) VALUES ('{drop_id}','{reaction.user_id}')")
                        break
                elif data is None: # No data, insert
                    await sql_do("uttcex_bot_db", f"INSERT INTO `airdrops_participants`(`drop_id`, `participant_id`) VALUES ('{drop_id}','{reaction.user_id}')")
                # Don't return to check finalize
                
    # Finalize drop
    xparticipants = await sql_select("uttcex_bot_db", "airdrops_participants", "*", "*")
    if xparticipants is None:
        # Return money to dropper
        # Delete airdrop from `airdrops`
        await backend_credit(int(dropper), amount, coin)
        await raw_unlock_bal(int(dropper), coin, amount)
        await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops` WHERE `drop_id` = '{drop_id}'")
        e = mx.embeds[0]
        e.description = f"Done, no users joined. Returned {format(amount, decidic[coin])} {emojis[coin]} to <@{data[0]}>"
        await mx.edit(embed = e)
        return
    participants = []
    for x in xparticipants:
        if x[0] == drop_id and int(x[1]) not in participants:
            participants.append(int(x[1]))
    total = len(participants)
    if total == 0 and Decimal(current_time) > Decimal(end_time):
        # Return money to dropper
        # Delete airdrop from `airdrops`
        await backend_credit(int(dropper), amount, coin)
        await raw_unlock_bal(int(dropper), coin, amount)
        await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops` WHERE `drop_id` = '{drop_id}'")
        e = mx.embeds[0]
        e.description = f"Done, no users joined. Returned {format(amount, decidic[coin])} {emojis[coin]} to <@{data[0]}>"
        await mx.edit(embed = e)
        return
    if total == max_participants and Decimal(current_time) <= Decimal(end_time):
        give = amount / total
        given = Decimal("0.0")
        places = len(format(atomdic[coin], decidic[coin]).replace("0.","").replace("f",""))
        round_factor = Decimal("1." + ("0" * places))
        give = give.quantize(round_factor, rounding=decimal.ROUND_DOWN)
        # Debit author, delete lock (even out), delete airdrop with drop ID, delete participant list with drop ID
        # Credit each user
        to_give = []
        index = 0
        while given + give <= Decimal(amount):
            xuser = participants[index % total]
            given += give
            to_give.append([xuser, format(give, decidic[coin]), coin])
            index += 1
        remainder = Decimal(amount) - given
        if remainder > 0:
            xuser = participants[index % total]
            to_give.append([xuser, format(remainder, decidic[coin]), coin])
        if (await raw_unlock_bal(dropper, coin, amount)) is False:
            await mx.edit("Airdrop failed, an unknown error occurred.\n\nSupport has been notified.")
            await support(mxr)
            return
        else:
            await backend_debit(dropper, amount, coin)
            await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops` WHERE `drop_id` = '{drop_id}'")
            await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops_participants` WHERE `drop_id` = '{drop_id}'")
            for entry in to_give:
                await backend_log_tip(dropper, entry[0], entry[1], coin) 
                await backend_credit(entry[0], Decimal(entry[1]), coin)
            e = mx.embeds[0]
            recipients = [f"<@{x[0]}>" for x in to_give]
            val = await get_price(coin)
            val = format(val * give, ',.12f')
            e.description = f"Done, {total} participants.\n\n{', '.join(recipients)}\n\nEach received **${val} USD**"
            await mx.edit(embed = e)
    elif (total <= max_participants) and (total > 0) and (Decimal(current_time) > Decimal(end_time)):
        give = amount / total
        given = Decimal("0.0")
        places = len(format(atomdic[coin], decidic[coin]).replace("0.","").replace("f",""))
        round_factor = Decimal("1." + ("0" * places))
        give = give.quantize(round_factor, rounding=decimal.ROUND_DOWN)
        # Debit author, delete lock (even out), delete airdrop with drop ID, delete participant list with drop ID
        # Credit each user
        to_give = []
        index = 0
        while given + give <= Decimal(amount):
            xuser = participants[index % total]
            given += give
            to_give.append([xuser, format(give, decidic[coin]), coin])
            index += 1
        remainder = Decimal(amount) - given
        if remainder > 0:
            xuser = participants[index % total]
            to_give.append([xuser, format(remainder, decidic[coin]), coin])
        if (await raw_unlock_bal(dropper, coin, amount)) is False:
            await mx.edit("Airdrop failed, an unknown error occurred.\n\nSupport has been notified.")
            await support(mxr)
            return
        else:
            await backend_debit(dropper, amount, coin)
            await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops` WHERE `drop_id` = '{drop_id}'")
            await sql_do("uttcex_bot_db", f"DELETE FROM `airdrops_participants` WHERE `drop_id` = '{drop_id}'")
            for entry in to_give:
                await backend_log_tip(dropper, entry[0], entry[1], coin) 
                await backend_credit(entry[0], Decimal(entry[1]), coin)
            e = mx.embeds[0]
            recipients = [f"<@{x[0]}>" for x in to_give]
            val = await get_price(coin)
            val = format(val * give, ',.12f')
            e.description = f"Done, {total} participants.\n\n{', '.join(recipients)}\n\nEach received **${val} USD**"
            await mx.edit(embed = e)
            return
        

# Not cached
@client.event
async def on_raw_reaction_remove(reaction):
    print("raw remove")
    mxid = reaction.message_id        # Reacted message ID
    mxchid = reaction.channel_id      # Reacted message channel ID
    ch = client.get_channel(mxchid)   # Channel of reacted message
    mx = await ch.fetch_message(mxid) # Reacted message
    mxr = mx.reference                # Reacted message replied to this
    mxrid = mx.reference.message_id   # Replied to message ID
    mxr = await ch.fetch_message(mxrid)
    origin_author = mxr.author
    if (int(reaction.user_id) == bot_ids[BOT_CFG_FLAG]["uttcex"]):
        return
    data = await sql_select("uttcex_bot_db", "airdrops", "*", "*")
    if data is not None:
        for drop in data:
            if Decimal(time.time()) > Decimal(drop[5]):
                return
            if int(drop[6]) == mxrid:
                if (reaction.emoji.id == emojid[drop[1]]):
                    return


### INTERNALS ###
#################
async def sanistr(s: str) -> str:
    safechars = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_=:.,*$?()"
    x = ""
    for y in s:
        if y in safechars:
            x += y
    return x.replace("   ", " ").replace("  ", " ")


async def randstr(length: int) -> str:
    return "".join(random.choice(rchars) for _ in range(length))


async def t_randstr(length: int) -> str:
    return "".join(random.choice(rchars) for _ in range(length))


async def get_coin_list() -> list:
    return [x[0] for x in coin_list]


def t_get_coin_list() -> list:
    return [x[0] for x in coin_list]


async def valid_coin(coin: str) -> bool:
    if ((await sanistr(coin)) in await get_coin_list()):
        return True
    return False


def heartbeat(s: str):
    t_gprint(f"\n[♥ Heartbeat ♥] {s}\n", "botleft", "log")
    return


# UTTCex Admin GUI!
async def gprint(s: str, w: str, l: str):
    global gui_log1
    global gui_log2
    match (l.lower()):
        case ("log"):
            match (w.lower()):
                case ("topleft"):
                    gui_log1.append([s, 0, False])
                    return
                case ("topright"):
                    gui_log1.append([s, 1, False])
                    return
                case ("botleft"):
                    gui_log1.append([s, 2, False])
                    return
                case ("botright"):
                    gui_log1.append([s, 3, False])
                    return
        case ("chat"):
            match (w.lower()):
                case ("topleft"):
                    gui_log2.append([s, 0, False])
                    return
                case ("topright"):
                    gui_log2.append([s, 1, False])
                    return
                case ("botleft"):
                    gui_log2.append([s, 2, False])
                    return
                case ("botright"):
                    gui_log2.append([s, 3, False])
                    return


def t_gprint(s: str, w: str, l: str):
    global gui_log1
    global gui_log2
    match (l.lower()):
        case ("log"):
            match (w.lower()):
                case ("topleft"):
                    gui_log1.append([s, 0, False])
                    return
                case ("topright"):
                    gui_log1.append([s, 1, False])
                    return
                case ("botleft"):
                    gui_log1.append([s, 2, False])
                    return
                case ("botright"):
                    gui_log1.append([s, 3, False])
                    return
        case ("chat"):
            match (w.lower()):
                case ("topleft"):
                    gui_log2.append([s, 0, False])
                    return
                case ("topright"):
                    gui_log2.append([s, 1, False])
                    return
                case ("botleft"):
                    gui_log2.append([s, 2, False])
                    return
                case ("botright"):
                    gui_log2.append([s, 3, False])
                    return


async def geprint(s: str, w: str, l: str):
    global gui_log1
    global gui_log2
    match (l.lower()):
        case ("log"):
            match (w.lower()):
                case ("topleft"):
                    gui_log1.append([s, 0, True])
                    return
                case ("topright"):
                    gui_log1.append([s, 1, True])
                    return
                case ("botleft"):
                    gui_log1.append([s, 2, True])
                    return
                case ("botright"):
                    gui_log1.append([s, 3, True])
                    return
        case ("chat"):
            match (w.lower()):
                case ("topleft"):
                    gui_log2.append([s, 0, True])
                    return
                case ("topright"):
                    gui_log2.append([s, 1, True])
                    return
                case ("botleft"):
                    gui_log2.append([s, 2, True])
                    return
                case ("botright"):
                    gui_log2.append([s, 3, True])
                    return


def t_geprint(s: str, w: str, l: str):
    global gui_log1
    global gui_log2
    match (l.lower()):
        case ("log"):
            match (w.lower()):
                case ("topleft"):
                    gui_log1.append([s, 0, True])
                    return
                case ("topright"):
                    gui_log1.append([s, 1, True])
                    return
                case ("botleft"):
                    gui_log1.append([s, 2, True])
                    return
                case ("botright"):
                    gui_log1.append([s, 3, True])
                    return
        case ("chat"):
            match (w.lower()):
                case ("topleft"):
                    gui_log2.append([s, 0, True])
                    return
                case ("topright"):
                    gui_log2.append([s, 1, True])
                    return
                case ("botleft"):
                    gui_log2.append([s, 2, True])
                    return
                case ("botright"):
                    gui_log2.append([s, 3, True])
                    return


locked = False
lock_toplevel = None


def uttcex_gui(ulog: list):
    global lock_toplevel
    lock = threading.Lock()
    gui = tk.Tk()
    tmp = []
    zoom_level = 0

    def lock_screen():
        global locked
        global lock_toplevel
        if (locked == False):
            locked = True
            lock_toplevel.attributes('-fullscreen', True)  # Cover the entire screen
            lock_toplevel.attributes('-topmost', True)  # Keep it on top
            lock_toplevel.title("Lock Screen")

            label = tk.Label(lock_toplevel, text="- UTTCex Mainframe Locked -")
            label.pack(pady=10)

            entry = tk.Entry(lock_toplevel, show="*")
            entry.pack(pady=5)

            submit_button = tk.Button(lock_toplevel, text="Unlock", command=lambda: unlock_screen(entry.get()))
            submit_button.pack(pady=10)

    # Function to unlock the screen
    def unlock_screen(password):
        global locked
        global lock_toplevel
        if password == "":  # Replace with your actual password
            locked = False
            lock_toplevel.attributes('-fullscreen', False)  # Stop covering the screen
            lock_toplevel.attributes('-topmost', False)  # Allow other things to take focus
            lock_toplevel.title("Lock Screen")

    def exit_application():
        shutdown = True
        gui.quit()  # Close the Tkinter window
        return

    # Example: Schedule adding messages to the chat log
    def schedule_messages():
        if (len(ulog) > 0):
            add_log(ulog[0][1], ulog[0][0], ulog[0][2])
            with lock:
                ulog.pop(0)
            gui.after(50, schedule_messages)
        else:
            gui.after(50, schedule_messages)
        return

    def insert(log: tk.Text, message: str):
        log.config(state=tk.NORMAL)  # Allow editing
        log.insert("end", f"{message}")  # Append
        log.config(state=tk.DISABLED)  # Disable editing
        log.yview_moveto(1.0)  # Scroll to the end
        return

    def add_log(window: int, message: str, e_status: bool):
        match (e_status):
            case (False):
                match (window):
                    case (0):  # Top Left
                        insert(log1, message)
                        return
                    case (1):  # Top Right
                        insert(log2, message)
                        return
                    case (2):  # Bottom Left
                        insert(log3, message)
                        return
                    case (3):  # Bottom Right
                        insert(log4, message)
                        return
            case (True):
                # message = "\u001b[0;40;31m" + message + "\u001b[0;0m"  # Make the message red
                match (window):
                    case (0):  # Top Left
                        insert(log1, message)
                        return
                    case (1):  # Top Right
                        insert(log2, message)
                        return
                    case (2):  # Bottom Left
                        insert(log3, message)
                        return
                    case (3):  # Bottom Right
                        insert(log4, message)
                        return

    # Function to handle mouse wheel event for scrolling the logs
    def scroll1(event):
        log1.yview_scroll(-1 * (event.delta // 120), "units")
        return

    def scroll2(event):
        log2.yview_scroll(-1 * (event.delta // 120), "units")
        return

    def scroll3(event):
        log3.yview_scroll(-1 * (event.delta // 120), "units")
        return

    def scroll4(event):
        log4.yview_scroll(-1 * (event.delta // 120), "units")
        return

    # Initialize our window
    ico_loaded = False
    match (ulog[0]):
        case (0):
            gui.title("UTTCex v5 GUI [UTTCex Logs]")  # Set the window title
            try:
                gui.iconbitmap("uttc.ico")
            except:
                time.sleep(5)
                gui.iconbitmap("uttc.ico")
            ulog.pop(0)
            ico_loaded = True
        case (1):
            gui.title("UTTCex v5 GUI [Chats]")  # Console Log
            try:
                gui.iconbitmap("uttc.ico")
            except:
                time.sleep(5)
                gui.iconbitmap("uttc.ico")
            ulog.pop(0)
            ico_loaded = True

    del ico_loaded

    gui.configure(bg="black")  # Set the background color to black
    gui.geometry("1536x750")  # Set the default size to 1000x750
    gui.resizable(False, False)  # Make the window non-resizable

    # GUI elements below

    # Create a menu bar
    menu_bar = tk.Menu(gui)
    gui.config(menu=menu_bar)
    lock_toplevel = tk.Toplevel(gui)

    # Create a File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.configure(bg="black", fg="white", activebackground="black", activeforeground="white")
    file_menu.add_command(label="Lock", command=lock_screen)
    menu_bar.add_cascade(label="Bot", menu=file_menu)

    # Add an "Exit" option to the File menu
    file_menu.add_command(label="Exit", command=exit_application)

    # Create an Edit menu (you can add more options as needed)
    edit_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Manage", menu=edit_menu)

    ####### GUI MAIN LOOP
    ######
    ####
    ##
    #

    # Create an empty container on the far left
    left_frame = tk.Frame(gui, bg="black")
    left_frame.place(x=0, y=0, width=512, height=750)

    # Create Log Container on Top Left
    log_container1 = tk.Frame(gui, bg="black")
    log_container1.place(x=512, y=0, width=512, height=375)
    log1 = tk.Text(log_container1, bg="black", fg="white", wrap=tk.WORD)
    log1.config(font=("Monaco", 10))
    log1.place(x=0, y=0, width=512, height=375)

    # Create Log Container on Top Right
    log_container2 = tk.Frame(gui, bg="black")
    log_container2.place(x=1024, y=0, width=512, height=375)
    log2 = tk.Text(log_container2, bg="black", fg="white", wrap=tk.WORD)
    log2.config(font=("Monaco", 10))
    log2.place(x=0, y=0, width=512, height=375)
    # chat_log.tag_configure("INFO", foreground="yellow")

    # Create Log Container on Bottom Left
    log_container3 = tk.Frame(gui, bg="black")
    log_container3.place(x=512, y=375, width=512, height=375)
    log3 = tk.Text(log_container3, bg="black", fg="white", wrap=tk.WORD)
    log3.config(font=("Monaco", 10))
    log3.place(x=0, y=0, width=512, height=375)

    # Create Log Container on Bottom Right
    log_container4 = tk.Frame(gui, bg="black")
    log_container4.place(x=1024, y=375, width=512, height=375)
    log4 = tk.Text(log_container4, bg="black", fg="white", wrap=tk.WORD)
    log4.config(font=("Monaco", 10))
    log4.place(x=0, y=0, width=512, height=375)

    # Bind the mouse wheel event to the zoom function
    log1.bind("<Control-MouseWheel>", scroll1)
    log2.bind("<Control-MouseWheel>", scroll2)
    log3.bind("<Control-MouseWheel>", scroll3)
    log4.bind("<Control-MouseWheel>", scroll4)

    schedule_messages()

    ######### GUI MAIN LOOP
    #########

    gui.mainloop()
    return

ipckey = os.getenv("UTTCEX_IPC_KEY")
challenge = "cn2h!(*@H3ncl(4)0000000000000000@nl9z6l:O3@800000000000000U7AL6:IC0-2|HB"

sol_address_list = []

class IPCRequestHandler(BaseHTTPRequestHandler):
    ipckey = os.getenv("UTTCEX_IPC_KEY")

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    # Handle GET requests
    def do_GET(self):
        self._set_headers()
        response = "<div style='border: thin solid black;width:500px;height:500px;'>Test</div>"
        self.wfile.write(response.encode())

    # Handle POST requests
    def do_POST(self):
        global scheduled_messages
        global sql_connected
        global sol_address_list
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())

        print("Received data:", data)

        # Decompress and decrypt data
        decompressed_key = zlib.decompress(bytes.fromhex(data["key"]))
        decrypted_key = b''
        try:
            decrypted_key = crypto.crypto.uttcex_ipc_decrypt(decompressed_key, ipckey, 35)
        except:
            print("Bad decryption!")

        enc_key = crypto.crypto.encrypt_compress(ipckey, ipckey, 35)

        if decrypted_key == ipckey:
            try:
                instruction = crypto.crypto.decompress_decrypt(data["instruction"], ipckey, 7)
                print(f"Instruction [{instruction}] received!")
                if instruction == "get_sol_addresses":
                    address_list = []
                    for addy in sol_address_list:
                        address_list.append(addy[0])
                    address_list = "\n".join(address_list)
                    enc_address_list = crypto.crypto.encrypt_compress(address_list, ipckey, 7)
                    response = json.dumps({'key': f'{enc_key.hex()}', 'result': f'{enc_address_list.hex()}'})
                    self._set_headers()
                    self.wfile.write(response.encode())
                    return
                elif instruction == "get_sql_connection_status":
                    sql_status = str(bool(sql_connected))
                    enc_sql_staatus = crypto.crypto.encrypt_compress(sql_status, ipckey, 7)
                    response = json.dumps({'key': f'{enc_key.hex()}', 'result': f'{enc_sql_status.hex()}'})
                    self._set_headers()
                    self.wfile.write(response.encode())
                    return
            except:
                pass
            try:
                    address_list = []
                    for addy in sol_address_list:
                        address_list.append(addy[0])
                    address_list = "\n".join(address_list)
                    print(address_list)
                    enc_address_list = crypto.crypto.encrypt_compress(address_list, ipckey, 7)
                    enc_key = crypto.crypto.encrypt_compress(ipckey, ipckey, 35)
                    response = json.dumps({'key': f'{enc_key.hex()}', 'result': f'{enc_address_list.hex()}'})
                    self._set_headers()
                    self.wfile.write(response.encode())
                    return
            except:
                pass
            try:
                print("DEPOSIT DETECTED")
                discord_id = crypto.crypto.decompress_decrypt(data["discord_id"], ipckey, 44)
                amount = crypto.crypto.decompress_decrypt(data["amount"], ipckey, 21)
                coin = crypto.crypto.decompress_decrypt(data["coin"], ipckey, 15)
                txid = crypto.crypto.decompress_decrypt(data["txid"], ipckey, 37)
                uttcex_id = udefs.udefs.t_get_uid(int(discord_id))
                data = t_sql_select("uttcex_bot_db", "profiles", "uttcex_id", uttcex_id)
                lang = ulang.ulang.profile_locale[int(data[23])]
                e = Embed(
                    title=f"{ulang.ulang.locale_msg[lang]['dm_deposit_title_1']} [{coin.upper()}] {ulang.ulang.locale_msg[lang]['dm_deposit_title_1']}",
                    description=f"{format(Decimal(amount) * atomdic[coin], decidic[coin])} {coin.upper()}",
                    color=0x00ff00)
                scheduled_messages.append([discord_id, coin, amount, txid, uttcex_id])  # DM the user (5 params)
                print("Appended deposit to queue.")
            except:
                pass


# Define the main function for the client thread
def deposit_monitor_client_thread():
    server_address = ('localhost', 55506)
    # Create an HTTP server
    httpd = HTTPServer(server_address, IPCRequestHandler)
    print('IPC server running...')
    while (True):
        httpd.serve_forever()
        print("IPC server restarted ...")
    return
    ##

def wallet_utxo_update_thread(coin: str):
    lock = threading.Lock()
    hb_name = f"[{coin.upper()}] Wallet UTXO Update Thread"
    global scheduled_messages
    global gui_log1
    global gui_log2
    while (True):
        # # #
        #
        # Check all incoming deposits here
        #
        # # #
        ttitle = f"[INFO] [{coin.upper()} THREAD]"
        # BITCOINLIB
        if ((coin == "btc") or (coin == "ltc") or (coin == "doge")):   # Bitcoinlib Coins
            w = bitcoinlib.wallets.Wallet(uwallet[coin])
            w.default_network_set(unetwork[coin])
            t_gprint(f"\n{ttitle} - Scanning UTXOs ...\n", "topright", "log")
            for utxo in w.utxos():
                address = utxo['address']
                amount = utxo['value']
                txid = utxo['txid']
                # Get the discord ID via their address and uttcex_id
                data = t_sql_select(wallet_db[coin], coin, "public_address", address)
                uttcex_id = data[4]
                data = t_sql_select("uttcex_bot_db", "profiles", "uttcex_id", uttcex_id)
                discord_id = data[18]
                lang = profile_locale[data[2]]
                # Check if TXID exists in DB, if not, add to DB
                data = t_sql_select(wallet_db[coin], f"{coin}_utxos", "tx_hash", f"{txid}")
                if data is None:                                                                 # TXID WAS NOT ADDED!!!
                    t_gprint(f"{ttitle} [UTXO]: Transaction output found!\n[DATA] [Receiving Address]: {address}\n[DATA] [Amount]: {format(Decimal(amount) * atomdic[coin], decidic[coin])} {coin.upper()}\n[DATA] [TXID]: {txid}", "topright", "log")
                    # Credit the deposit
                    t_sql_insert(wallet_db[coin], f"{coin}_utxos", "tx_hash", f"{txid}")
                    t_sql_update(wallet_db[coin], f"{coin}_utxos", "sat_amount", f"{amount}", "tx_hash", f"{txid}")
                    t_sql_update(wallet_db[coin], f"{coin}_utxos", "receiving_address", f"{address}", "tx_hash", f"{txid}")
                    e = discord.Embed(title = f"{locale_msg[lang]['dm_deposit_title_1']} [{coin.upper()}] {locale_msg[lang]['dm_deposit_title_1']}", description = f"{format(Decimal(amount) * atomdic[coin], decidic[coin])} {coin.upper()}", color = 0x00ff00)
                    scheduled_messages.append([e, discord_id, coin, txid, uttcex_id]) # DM the user (5 params)
                elif data is not None:
                    if ((data[3] == "0") and (data[0] is not None)):                             # Logged but not credited???
                        t_gprint(f"{ttitle} [UTXO]: Transaction output found!\n[DATA] [Receiving Address]: {address}\n[DATA] [Amount]: {format(Decimal(amount) * atomdic[coin], decidic[coin])} {coin.upper()}\n[DATA] [TXID]: {txid}", "topright", "log")
                        # Credit the deposit
                        t_sql_update(wallet_db[coin], f"{coin}_utxos", "sat_amount", f"{amount}", "tx_hash", f"{txid}")
                        t_sql_update(wallet_db[coin], f"{coin}_utxos", "receiving_address", f"{address}", "tx_hash", f"{txid}")
                        t_sql_update(wallet_db[coin], f"{coin}_utxos", "credited", f"1", "tx_hash", f"{txid}")
                        e = discord.Embed(title = f"{locale_msg[lang]['dm_deposit_title_1']} [{coin.upper()}] {locale_msg[lang]['dm_deposit_title_1']}", description = f"{format(Decimal(amount) * atomdic[coin], decidic[coin])} {coin.upper()}", color = 0x00ff00)
                        scheduled_messages.append([e, discord_id, coin, txid, uttcex_id]) # DM the user (5 params)
                else: # It has been credited.
                    t_gprint(f"{ttitle} - Scan complete!\n", "topright", "log")
                    heartbeat(hb_name + f"")
                    time.sleep(60)
                    continue
            try:
                w.utxos_update()        # Update the UTXOs after we scan the current.
            except:
                t_gprint(f"{ttitle} [-EXCEPTION-] Re-Scanning UTXOs ...\n", "left", "log")
                continue
        # WEB3 SMART CHAINS
        elif ((coin == "eth") or (coin == "matic") or (coin == "bnb") or (coin == "op") or (coin == "avax")):
            t_gprint(f"\n{ttitle} - Scanning UTXOs ...\n", "topright", "log")
            addresses = t_sql_select(wallet_db[coin], coin, "public_address", "*") # Get all addresses on file
            if (addresses == None):
                t_gprint(f"{ttitle} - Scan complete!\n", "topright", "log")
                heartbeat(hb_name + f"")
                time.sleep(60)
                continue
            w3 = web3.Web3(web3.HTTPProvider(web3network[coin]))
            for address in addresses:
                api_url = ""
                match (coin):
                    case ("eth"):
                        api_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey=JY8BVWUB1R54M382P2UA1EWGA8QT86UXJQ"
                    case ("matic"):
                        api_url = f"https://api.polygonscan.com/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey=ASJTUV5JYCCP1QEK1DYHW445IZCATMDEA7"
                    case ("bnb"):
                        api_url = f"https://api.bscscan.com/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey=6XE8C2KIIBQTJD7Q8G2M1RNF8UIKAI1RHU"
                    case ("op"):
                        api_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey=JY8BVWUB1R54M382P2UA1EWGA8QT86UXJQ"
                    case ("avax"):
                        api_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey=JY8BVWUB1R54M382P2UA1EWGA8QT86UXJQ"
                r = None
                try:
                    r = requests.get(api_url)
                except:
                    t_gprint(f"{ttitle} - Scan complete!\n", "topright", "log")
                    heartbeat(hb_name + f"")
                    time.sleep(60)
                    continue
                if r.status_code == 200:
                    txs = r.json()['result']
                    for tx in txs:
                        txid = ""
                        try:
                            txid = tx['hash']
                        except:
                            continue
                        if tx['to'].lower() != address.lower():
                            continue
                        # Get the discord ID via their address and uttcex_id
                        data = t_sql_select(wallet_db[coin], coin, "public_address", address)
                        uttcex_id = data[4]
                        data = t_sql_select("uttcex_bot_db", "profiles", "uttcex_id", uttcex_id)
                        discord_id = data[18]
                        lang = profile_locale[data[2]]
                        data = t_sql_select(wallet_db[coin], f"{coin}_utxos", "tx_hash", f"{txid}")
                        if data is None:
                            if tx["to"].lower() == address.lower(): # Credit the deposit
                                address = tx['to'].upper()
                                amount = int(tx['value'])
                                t_gprint(f"{ttitle} [UTXO]: Transaction output found!\n[DATA] [Receiving Address]: {address}\n[DATA] [Amount]: {format(t_from_atomic(coin, amount), decidic[coin])} {coin.upper()}\n[DATA] [TXID]: {txid}", "topright", "log")
                                t_sql_insert(wallet_db[coin], f"{coin}_utxos", "tx_hash", f"{txid}")
                                t_sql_update(wallet_db[coin], f"{coin}_utxos", "atom_amount", f"{amount}", "tx_hash", f"{txid}")
                                t_sql_update(wallet_db[coin], f"{coin}_utxos", "receiving_address", f"{address}", "tx_hash", f"{txid}")
                                e = discord.Embed(title = f"{locale_msg[lang]['dm_deposit_title_1']} [{coin.upper()}] {locale_msg[lang]['dm_deposit_title_1']}", description = f"{format(Decimal(amount) * atomdic[coin], decidic[coin])} {coin.upper()}", color = 0x00ff00)
                                scheduled_messages.append([e, discord_id, coin, txid, uttcex_id]) # DM the user (5 params)
                        elif data is not None:
                            if ((data[3] == "0") and (data[0] is not None)):                             # Logged but not credited???
                                address = tx['to'].upper()
                                amount = int(tx['value'])
                                t_gprint(f"{ttitle} [UTXO]: Transaction output found!\n[DATA] [Receiving Address]: {address}\n[DATA] [Amount]: {format(t_from_atomic(coin, amount), decidic[coin])} {coin.upper()}\n[DATA] [TXID]: {txid}", "topright", "log")
                                t_sql_update(wallet_db[coin], f"{coin}_utxos", "atom_amount", f"{amount}", "tx_hash", f"{txid}")
                                t_sql_update(wallet_db[coin], f"{coin}_utxos", "receiving_address", f"{address}", "tx_hash", f"{txid}")
                                t_sql_update(wallet_db[coin], f"{coin}_utxos", "credited", "1", "tx_hash", f"{txid}")
                                e = discord.Embed(title = f"{locale_msg[lang]['dm_deposit_title_1']} [{coin.upper()}] {locale_msg[lang]['dm_deposit_title_1']}", description = f"{format(Decimal(amount) * atomdic[coin], decidic[coin])} {coin.upper()}", color = 0x00ff00)
                                scheduled_messages.append([e, discord_id, coin, txid, uttcex_id]) # DM the user (5 params)
                        else:
                            pass
        elif (coin == "sol"):
            t_gprint(f"\n{ttitle} - Scanning UTXOs ...\n", "topright", "log")
            addresses = t_sql_select(wallet_db[coin], coin, "public_address", "*")  # Get all addresses on file
            if (addresses == None):
                t_gprint(f"{ttitle} - ERR_NO_ADDR Scan complete!\n", "topright", "log")
                heartbeat(hb_name + f"")
                time.sleep(3600)
                continue
            for address in addresses:
                time.sleep(5) # Self rate limit
                ntxs = sol_client.get_signatures_for_address(solathon.PublicKey(address))
                for tx in ntxs:
                    txid = tx.signature
                    d1 = t_sql_select(wallet_db["sol"], f"sol_utxos", "tx_hash", f"{txid}")
                    d2 = t_sql_select(wallet_db["sol"], f"sol_utxos", "fluffy_tx_hash", f"{txid}")
                    if ((d1 is not None) or (d2 is not None)):  # Save a call if TX exists
                        continue
                    time.sleep(5) # Self rate limit
                    tx = sol_client.get_transaction(txid)
                    amount = tx.meta.post_balances[1] - tx.meta.pre_balances[1]
                    if amount == 0: # Token, change coin to token name found
                        # We're redirecting the TXID to whatever token it is related to,
                        # therefore when using the token we refer to it the same way we
                        # access it in the following manner:
                        if tx.meta.post_token_balances[1]["mint"] == "F2cexxKrSsVk7XsQk1rBUV7UpLyDRU3eip1w6YCri37C": # FLUFFY
                            pre = None
                            try:
                                pre = Decimal(tx.meta.pre_token_balances[1]["uiTokenAmount"]["amount"])
                            except:  # No pre-balance
                                pre = Decimal("0.0")
                            post = Decimal(tx.meta.post_token_balances[1]["uiTokenAmount"]["amount"])
                            amount = Decimal(str(int(post - pre)))
                            # Get the discord ID via their address and uttcex_id
                            data = t_sql_select(wallet_db["sol"], "sol", "public_address", address)
                            uttcex_id = data[4]
                            data = t_sql_select("uttcex_bot_db", "profiles", "uttcex_id", uttcex_id)
                            discord_id = data[18]
                            lang = profile_locale[data[2]]
                            if ((d1 is None) and (d2 is None)): # Cannot be in either TX record
                                t_gprint(
                                    f"{ttitle} [UTXO]: Transaction output found!\n[DATA] [Receiving Address]: {address}\n[DATA] [Amount]: {format(t_from_atomic(coin, amount), decidic[coin])} {coin.upper()}\n[DATA] [TXID]: {txid}",
                                    "topright", "log")
                                t_sql_insert(wallet_db["sol"], f"sol_utxos", "fluffy_tx_hash", f"{txid}")
                                t_sql_update(wallet_db["sol"], f"sol_utxos", "fluffy_atom_amount", f"{amount}", "fluffy_tx_hash", f"{txid}")
                                t_sql_update(wallet_db["sol"], f"sol_utxos", "receiving_address", f"{address}", "fluffy_tx_hash", f"{txid}")
                                e = discord.Embed(
                                    title=f"{locale_msg[lang]['dm_deposit_title_1']} [{coin.upper()}] {locale_msg[lang]['dm_deposit_title_1']}",
                                    description=f"{format(Decimal(amount) * atomdic[coin], decidic[coin])} {coin.upper()}",
                                    color=0x00ff00)
                                scheduled_messages.append([e, discord_id, coin, txid, uttcex_id])  # DM the user (5 params)
                                continue
                            else:
                                continue
                    # Get the discord ID via their address and uttcex_id
                    if (coin == "sol"):
                        data = t_sql_select(wallet_db[coin], coin, "public_address", address)
                        uttcex_id = data[4]
                        data = t_sql_select("uttcex_bot_db", "profiles", "uttcex_id", uttcex_id)
                        discord_id = data[18]
                        lang = profile_locale[data[2]]
                        data = t_sql_select(wallet_db[coin], f"{coin}_utxos", "tx_hash", f"{txid}")
                        if ((d1 is None) and (d2 is None)): # Cannot be in either TX record
                            t_gprint(
                                f"{ttitle} [UTXO]: Transaction output found!\n[DATA] [Receiving Address]: {address}\n[DATA] [Amount]: {format(t_from_atomic(coin, amount), decidic[coin])} {coin.upper()}\n[DATA] [TXID]: {txid}",
                                "topright", "log")
                            t_sql_insert(wallet_db[coin], f"{coin}_utxos", "tx_hash", f"{txid}")
                            t_sql_update(wallet_db[coin], f"{coin}_utxos", "atom_amount", f"{amount}", "tx_hash", f"{txid}")
                            t_sql_update(wallet_db[coin], f"{coin}_utxos", "receiving_address", f"{address}", "tx_hash",
                                         f"{txid}")
                            e = discord.Embed(
                                title=f"{locale_msg[lang]['dm_deposit_title_1']} [{coin.upper()}] {locale_msg[lang]['dm_deposit_title_1']}",
                                description=f"{format(Decimal(amount) * atomdic[coin], decidic[coin])} {coin.upper()}",
                                color=0x00ff00)
                            scheduled_messages.append([e, discord_id, coin, txid, uttcex_id])  # DM the user (5 params)
                            continue
        elif (coin == "uttc"):
            t_gprint(f"{ttitle} - Scan complete!\n", "topright", "log")
            heartbeat(hb_name + f"")
            time.sleep(300)
            continue
        elif (coin == "xmr"):
            t_gprint(f"{ttitle} - Scan complete!\n", "topright", "log")
            heartbeat(hb_name + f"")
            time.sleep(300)
            continue
        elif (coin == "xrp"):
            t_gprint(f"{ttitle} - Scan complete!\n", "topright", "log")
            heartbeat(hb_name + f"")
            time.sleep(300)
            continue
        t_gprint(f"{ttitle} - Scan complete!\n", "topright", "log")
        heartbeat(hb_name + f"")
        time.sleep(300)
    return


def balance_discrepancy():
    global waenabled
    global active_discrepancy
    hb_name = f"Balance Sanity Thread"
    while (True):
        cleared = 0
        count = 0
        for coin in (t_get_coin_list()):
            instant_bals = None
            if (coin == "fluffy"):
                instant_bals = t_sql_select(wallet_db["sol"], "sol", "fluffy_instant_balance", "*")
            else:
                instant_bals = t_sql_select(wallet_db[coin], coin, "instant_balance", "*")
            cred = Decimal(0.0)
            ax = False
            ay = False
            if (instant_bals == None):
                ax = True
            else:
                for bal in instant_bals:
                    if bal == "":
                        bal = Decimal("0.0")
                    cred += Decimal(bal)
            utxo_bals = []
            if (coin != "fluffy"):
                utxo_bals = t_sql_select(wallet_db[coin], f"{coin}_utxos", "atom_amount", "*")
            if (coin == "fluffy"):
                utxo_bals = t_sql_select(wallet_db["sol"], "sol_utxos", "fluffy_atom_amount", "*")
            real = Decimal(0.0)
            if (utxo_bals == None):
                ay = True
            else:
                for bal in utxo_bals:
                    if bal == "":
                        bal = Decimal("0.0")
                    real += Decimal(format(t_from_atomic(coin, int(bal)), decidic[coin]))
            disc = Decimal(real - cred)
            s = ""
            if ((ax == True) and (ay == True)) or (
                    format(float(abs(disc)), decidic[coin]) == (format(0.0, decidic[coin]))):
                s = f"[✅ No Discrepancies Found] [-{coin.upper()}-]\n"
                cleared += 1
                count += 1
            elif (format(float(abs(disc)), decidic[coin]) != (format(0.0, decidic[coin]))):
                waenabled = False  # Immediately lock wallets and keep them locked, no need to do any evaluation before this. This is priority, then we can determine what we owe or are owed.
                active_discrepancy = True  # Set discrepancy state flag to true as well
                if (real < cred):  # Too many credits in circulation, must deduct them
                    s = f"[❌ Discrepancy Excess] [-{coin.upper()}-]: [+{format(abs(disc), decidic[coin])}]\n"
                elif (cred < real):  # Too few credits in circulation, must give them
                    s = f"[❌ Discrepancy Owed] [-{coin.upper()}-]: [-{format(abs(disc), decidic[coin])}]\n"
                e = Embed(title = "Security Log", description = f"```ansi\n\u001b[0;40;31mACTIVE DISCREPANCY\u001b[0;0m```\n**Core disabled.**\n\n### {s}", color = 0x00ff00)
                count += 1
            if ((cleared == count) and (active_discrepancy == True) and (count == len(t_get_coin_list()))):
                # Auto turn-off
                active_discrepancy = False
                waenabled = True
                t_gprint("[✅ Discrepancy Cleared]\n", "botright", "log")
                e = Embed(title = "Security Log", description = "Discrepnacies have been cleared.\n\nCore enabled automatically.", color = 0x00ff00)
            t_gprint(s, "botright", "log")
        heartbeat(hb_name + f"")
        continue
    return


def exchange_stats_update_thread():
    hb_name = f"[EXCHANGE] Channel Name Stats Update Thread"
    while (True):
        heartbeat(hb_name + f"")
        time.sleep(300)
    return


def price_update_thread():
    hb_name = f"[PRICE CHECK] Coin Price Update Thread"
    # print(coingecko.get_coins_list())
    while (True):
        t_gprint("\n[INFO] Getting prices from CoinGecko ...\n", "topleft", "log")
        x = time.time()
        count = 0
        # We have the coin list, now to zero in on the loop to get the prices.
        for coin in t_get_coin_list():
            cc = gcucoin_map[coin]
            p = coingecko.get_price(ids=f"{cc}", vs_currencies="usd")
            if coin == "fluffy":
                continue
            pp = format(Decimal(str(p[gcucoin_map[coin]]['usd'])), ".8f")
            try:
                t_sql_update(wallet_db[coin], "prices", f"{cc}", f"{pp}", "row_id", "0")
                t_geprint(f"\n[{cc}] Price updated! ({pp})\n", "topleft", "log")
            except:
                t_geprint(f"\n[{cc}] Failed to update price.\n", "topleft", "log")
            count += 1
        y = time.time() - x  # Measure the time
        # Complete
        t_gprint(
            f"[INFO] Price list obtained and DB updated.\n[INFO] [TIME] {y} seconds\n[INFO] Coin prices obtained: {count}\n",
            "topleft", "log")
        heartbeat(hb_name + f"")
        time.sleep(120)
    return


def database_backup_manager():
    backup_timer = 86400  # Every day, cause every hour was generating 2GB, may become larger, or smaller depending on optimizations.
    hb_name = f"[-Database Backup-]"
    data = t_sql_select("uttcex_bot_db", "config", "*", "*")
    if (data is None):  # Insert first backup
        back_time = str(time.time())
        name = "MAIN_" + str(back_time).replace(".", "_")
        os.system(f"@mkdir D:\\UTTCexDBBackup\\0_{name}")
        os.system(f"xcopy.exe /y /e /s C:\\xampp\\mysql D:\\UTTCexDBBackup\\0_{name}")
        t_sql_insert("uttcex_bot_db", "config", "last_db_backup", back_time)
        t_sql_update("uttcex_bot_db", "config", "last_backup_id", "0", "last_db_backup", back_time)
        time.sleep(backup_timer)
    while (True):  # Since data won't be None, this backs up every restart.
        last_time = t_sql_select("uttcex_bot_db", "config", "last_db_backup", "*")
        last_time = float(last_time[0])
        if (time.time() < last_time + backup_timer):  # Stop from every restart, so we don't generate GBs of data
            sleepy = math.floor(time.time() - last_time)
            time.sleep(sleepy)
            continue
        last_id = t_sql_select("uttcex_bot_db", "config", "last_backup_id", "*")
        if last_id != [""]:
            last_id = int(last_id[0])
        else:
            last_id = 0
        new_id = last_id + 1
        name = "MAIN_" + str(time.time()).replace(".", "_")
        back_time = str(time.time())
        os.system(f"@mkdir D:\\UTTCexDBBackup\\{new_id}_{name}")
        os.system(f"xcopy.exe /y /e /s C:\\xampp\\mysql D:\\UTTCexDBBackup\\{new_id}_{name}")
        t_sql_update("uttcex_bot_db", "config", "last_db_backup", back_time, "last_backup_id", f"{last_id}")
        t_sql_update("uttcex_bot_db", "config", "last_backup_id", f"{new_id}", "last_db_backup", back_time)
        time.sleep(backup_timer)
        continue
    return


async def stripid(tid) -> str:
    try:
        return str(tid).replace("<", "").replace(">", "").replace("@", "").replace("#", "")
    except:
        return str(tid)


async def rstr(l: int, mode: int) -> str:
    match (mode):
        case (0):
            return "".join(
                random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_=:.") for _ in range(l))
        case (1):  # DB-strict
            return "".join(
                random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(l))


async def status_flag(f: bool) -> str:
    # NOT TO BE CONFUSED WITH OTHER FLAG SETTING METHODS, THIS IS MERELY FOR status(discord.Message) THE COMMAND
    if f == True:
        return "✅ Enabled"
    return "❌ Disabled"


async def is_cmd(c: str) -> bool:
    if c.lower() in cmd_strlist:
        return True
    return False


async def get_auth(tid) -> str:
    # Do they have a profile?
    data = await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(tid))
    if data is None:
        await sql_insert("uttcex_bot_db", "profiles", "discord_id", await stripid(tid))
        return "0"
    return int(data[1])


async def has_auth(msg: discord.Message) -> bool:
    tmp = await sanistr(msg.content.lower())
    tmp = list(tmp[2:].split(" "))[0]
    for x, y in enumerate(cmd_list):
        if y[0] == tmp:
            req = int(cmd_list[x][1])
            auth = await get_auth(msg.author.id)
            if auth >= req:
                return True
    return False


async def has_profile(tid) -> bool:
    # Do they have a profile?
    data = await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(tid))
    if data is None:
        await sql_insert("uttcex_bot_db", "profiles", "discord_id", await stripid(tid))
        # Make their UTTCex ID
        data = await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(tid))
        while (True):
            uttcex_id = await rstr(10, 0)
            check = await sql_select("uttcex_bot_db", "profiles", "uttcex_id", uttcex_id)
            if check is None:
                await sql_update("uttcex_bot_db", "profiles", "uttcex_id", uttcex_id, "discord_id", await stripid(tid))
                break
        return True
    return True


async def has_server(sid) -> bool:
    # Does the server have a config?
    data = await sql_select("uttcex_bot_db", "servers", "server_id", await stripid(sid))
    if data is None:
        await sql_insert("uttcex_bot_db", "servers", "server_id", await stripid(sid))
        return True
    return True


async def has_wallet(tid, coin: str) -> bool:
    # Does the user have a wallet?
    if (await has_profile(tid) == True):  # Sanity check
        pass
    uttcex_id = await udefs.udefs.get_uid(int(tid))
    coin = alias[coin]
    # BITCOINLIB
    if ((coin == "btc") or (coin == "ltc") or (coin == "doge")):  # Bitcoinlib
        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
        if data is None:
            # Create the wallet
            w = bitcoinlib.wallets.Wallet(uwallet[coin])
            w.default_network_set(unetwork[coin])
            w.new_key(f"{uttcex_id}")  # key_name
            k = w.key(f"{uttcex_id}")  # key_name
            wif = k.wif  # For HDKey.from_wif()
            await sql_insert(wallet_db[coin], coin, "key_name", uttcex_id)
            await sql_update(wallet_db[coin], coin, "private_key", wif, "key_name", uttcex_id) # If wif_key gets renamed to private_key, we can summarize the DB and code here
            await sql_update(wallet_db[coin], coin, "public_address", k.address, "key_name", uttcex_id)
            return True
        elif data is not None:
            if data[0] == "" and data[1] == "" and data[3] != "" and data[4] != "": # For wallet regeneration
                # Create the wallet
                w = bitcoinlib.wallets.Wallet(uwallet[coin])
                w.default_network_set(unetwork[coin])
                w.new_key(f"{uttcex_id}")  # key_name
                k = w.key(f"{uttcex_id}")  # key_name
                wif = k.wif  # For HDKey.from_wif()
                await sql_update(wallet_db[coin], coin, "private_key", wif, "key_name", uttcex_id) # If wif_key gets renamed to private_key, we can summarize the DB and code here
                await sql_update(wallet_db[coin], coin, "public_address", k.address, "key_name", uttcex_id)
                return True
            return True
    # WEB3 BASE CHAINS
    elif ((coin == "eth") or (coin == "matic") or (coin == "bnb") or (coin == "op") or (coin == "avax")):
        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
        if data is None:
            # Create the wallet
            w3 = web3.Web3(web3.HTTPProvider(web3network[coin]))
            rstr = os.urandom(32)
            w = w3.eth.account.create(rstr)
            wkey = str(w._private_key.hex())
            waddy = str(w.address)
            await sql_insert(wallet_db[coin], coin, "key_name", uttcex_id)
            await sql_update(wallet_db[coin], coin, "private_key", wkey, "key_name", uttcex_id)
            await sql_update(wallet_db[coin], coin, "public_address", waddy, "key_name", uttcex_id)
            return True
        else:
            return True
    # WEB3 TOKENS - EVM CHAIN
    elif ((coin == "usdc") or (coin == "usdt") or (coin == "shib") or (coin == "pussy") or (coin == "cds")):
        if (await has_wallet(tid, "eth")) is True:
            pass
        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
        if data is None:
            wkey = await udefs.udefs.get_evm_key_from_uid(uttcex_id)
            waddy = await udefs.udefs.get_evm_address_from_uid(uttcex_id)
            await sql_insert(wallet_db[coin], coin, "key_name", uttcex_id)
            await sql_update(wallet_db[coin], coin, "private_key", wkey, "key_name", uttcex_id)
            await sql_update(wallet_db[coin], coin, "public_address", waddy, "key_name", uttcex_id)
            return True
        else:
            return True
    # WEB3 TOKENS - BSC CHAIN
    elif ((coin == "busd")):
        if (await has_wallet(tid, "bnb")) is True:
            pass
        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
        if data is None:
            wkey = await udefs.udefs.get_bsc_key_from_uid(uttcex_id)
            waddy = await udefs.udefs.get_bsc_address_from_uid(uttcex_id)
            await sql_insert(wallet_db[coin], coin, "key_name", uttcex_id)
            await sql_update(wallet_db[coin], coin, "private_key", wkey, "key_name", uttcex_id)
            await sql_update(wallet_db[coin], coin, "public_address", waddy, "key_name", uttcex_id)
            return True
        else:
            return True
    elif (coin == "xrp"):
        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
        if data is None:
            w = xrpl.wallet.Wallet.create()
            wkey = w.seed
            waddy = w.classic_address
            await sql_insert(wallet_db[coin], coin, "key_name", uttcex_id)
            await sql_update(wallet_db[coin], coin, "private_key", wkey, "key_name", uttcex_id)
            await sql_update(wallet_db[coin], coin, "public_address", waddy, "key_name", uttcex_id)
            return True
        else:
            return True
    elif (coin == "sol"):
        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
        if data is None:
            w = solathon.Keypair()
            private_key = w.private_key
            public_key = w.public_key
            await sql_insert(wallet_db[coin], coin, "key_name", uttcex_id)
            await sql_update(wallet_db[coin], coin, "private_key", private_key, "key_name", uttcex_id)
            await sql_update(wallet_db[coin], coin, "public_address", public_key, "key_name", uttcex_id)
            return True
        else:
            return True
    # SOL CHAIN - TOKENS
    elif (coin == "fluffy"): # Create token address
        if (await has_wallet(tid, "sol")) is True:
            pass
        # Get token address and create DB entry
        private_key = await udefs.udefs.get_sol_key_from_uid(uttcex_id)
        public_key = await udefs.udefs.get_sol_address_from_uid(uttcex_id)
        token_accounts = udefs.coindefs.sol_client.get_token_accounts_by_owner(public_key, mint_id = sol_token_mint[coin])
        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
        if data is None:
            for account_info in token_accounts:
                account_pubkey = account_info.pubkey
                await sql_insert(wallet_db[coin], coin, "key_name", uttcex_id)
                await sql_update(wallet_db[coin], coin, "private_key", private_key, "key_name", uttcex_id)
                await sql_update(wallet_db[coin], coin, "public_address", account_pubkey, "key_name", uttcex_id)
                print(f"SOL token account created. [{coin.upper()}] Address: {account_pubkey}")
                return True
            # Token account not created yet, may need instant coins
            await sql_insert(wallet_db[coin], coin, "key_name", uttcex_id)
            print(f"Temp SOL token account created. [{coin.upper()}] Address: (UID) {uttcex_id}")
            return True
        else:
            if data[0] == "" and data[1] == "" and data[3] != "": # Temp SOL token account
                return True
            else:
                return True


async def is_banned(tid) -> bool:
    if (await has_profile(tid) == True):
        data = await sql_select("uttcex_bot_db", "profiles", "discord_id", tid)
        if data is None: # Patch fix for users pre- default 0 value for DB
            await sql_update("uttcex_bot_db", "profiles", "is_banned", "0", "discord_id", tid)
        try:
            if data[3] == "1":
                return True
        except:
            return False


async def get_price(coin: str) -> Decimal:
    if coin == "fluffy":
        solprice = await sql_select(wallet_db["sol"], "prices", gcucoin_map["sol"], "*")
        solprice = Decimal(solprice[0])
        amtsol = Decimal("0.0000002")
        return Decimal(solprice * amtsol)
    data = await sql_select(wallet_db[coin], "prices", gcucoin_map[coin], "*")
    return Decimal(data[0])


### INTERNALS ###

# Get/Give chat exp #
async def chat_exp(msg: discord.Message):
    data = await sql_select("uttcex_bot_db", "profiles", "discord_id", msg.author.id)
    match (b):
        case (True):
            if (d[9] == "False"):
                return
            # Add exp
            match (b):
                case (True):
                    e = discord.Embed(title="Level Up!",
                                      description=f"You've gained a level from chatting!\n\n*You earn experience points in all servers hosting {udefs.umention}*\n- even if the host hasn't enabled level-up messages.",
                                      color=0x00ff00)
                    await msg.reply(embed=e)
                case (False):
                    return
        case (False):
            if (d[9] == "False"):
                return
            # Add exp
            match (b):
                case (True):
                    e = discord.Embed(title="Level Up!",
                                      description=f"You've gained a level from chatting!\n\n*You earn experience points in all servers hosting {udefs.umention}*\n- even if the host hasn't enabled level-up messages.",
                                      color=0x00ff00)
                    await msg.reply(embed=e)
                case (False):
                    return


### ERROR ###
async def err(index: int, p: list):
    lang = profile_locale[
        (await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(p[0].author.id)))[2]]
    e = discord.Embed(title=f"{locale_msg[lang]['error']}", description="", color=0xff0000)
    match (index):
        case (-3):  # Banned
            e.title = f"{locale_msg[lang]['platform_ban']}"
            e.description = f"{locale_msg[lang]['you_have_been_banned']}"
            await ereply(p[0], e)
            return
        case (-2):  # Not Whitelisted
            e.description = f"{locale_msg[lang]['server_whitelist_required']}"
            await ereply(p[0], e)
            return
        case (-1):  # Custom error
            e.description = f"{p[1]}"
            await ereply(p[0], e)
            return
        case (0):  # Invalid
            e.description = f"{locale_msg[lang]['invalid_command']}\n`{p[1]}` {locale_msg[lang]['is_not_valid_command']}"
            await ereply(p[0], e)
            return
        case (1):  # Unauthorized
            if lang == profile_locale["1"]: # German requires grammar correction
                e.description = f"{locale_msg[lang]['unauthorized']} `{p[1]}` {locale_msg[lang]['unauthorized_de_grammar_correction']}."
            else:
                e.description = f"{locale_msg[lang]['unauthorized']} `{p[1]}`."
            await ereply(p[0], e)
            return
        case (2):  # Bad parameter count
            if (p[2] == 0):
                return
            if lang == profile_locale["1"]: # German requires grammar correction
                e.description = f"{locale_msg[lang]['bad_param_count']}\n{locale_msg[lang]['you_typed']}: `{p[1]}` {locale_msg[lang]['you_typed_de_grammar_correction']}\n{locale_msg[lang]['expected_param_count']}: `{p[2]}`\n{locale_msg[lang]['number_param_given']}: `{p[3]}`"
            else:
                e.description = f"{locale_msg[lang]['bad_param_count']}\n{locale_msg[lang]['you_typed']}: `{p[1]}`\n{locale_msg[lang]['expected_param_count']}: `{p[2]}`\n{locale_msg[lang]['number_param_given']}: `{p[3]}`"
            await ereply(p[0], e)
            return
        case (3):  # Bad parameter
            if lang == profile_locale["1"]: # German requires grammar correction
                e.description = f"{locale_msg[lang]['you_typed']}: `{p[0].content}` {locale_msg[lang]['you_typed_de_grammar_correction']}\n{locale_msg[lang]['bad_param_index']}: `{p[2]}` **::** `{p[1]}`"
            else:
                e.description = f"{locale_msg[lang]['you_typed']}: `{p[0].content}`\n{locale_msg[lang]['bad_param_index']}: `{p[2]} :: {p[1]}`"
            await ereply(p[0], e)
            return
        case (4):  # Private profile
            e.description = f"{locale_msg[lang]['profile_is_private']}"
            await ereply(p[0], e)
            return
        case (5):  # Operation failed.
            e.description = f"{locale_msg[lang]['operation_failed']}"
            await ereply(p[0], e)
            return
        case (6):  # Wallets disabled.
            e.description = f"{locale_msg[lang]['wallets_disabled']}"
            await ereply(p[0], e)
            return
        case (7):  # Insufficient balance.
            e.description = f"{locale_msg[lang]['insufficient_balance']}"
            await ereply(p[0], e)
            return
        case (8):  # Amount too low.
            e.description = f"{locale_msg[lang]['amount_too_low']}"
            await ereply(p[0], e)
            return
        case (9):  # Too early.
            e.description = f"{locale_msg[lang]['too_early']}"
            await ereply(p[0], e)
            return
        case (10):  # Cannot tip self
            e.description = f"{locale_msg[lang]['cant_tip_self']}"
            await ereply(p[0], e)
            return
        case (11):  # Cannot tip Tip.cc
            if lang == profile_locale["1"]: # German requires grammar correction
                e.description = f"{locale_msg[lang]['cant_send_tips_to']} <@{bot_ids[BOT_CFG_FLAG]['tipcc']}> {locale_msg[lang]['cant_send_tips_to_de_grammar_correction']}.\n\n<@{bot_ids[BOT_CFG_FLAG]['tipcc']}> {locale_msg[lang]['does_not_support_tips']} <@{bot_ids[BOT_CFG_FLAG]['uttcex']}>."
            else:
                e.description = f"{locale_msg[lang]['cant_send_tips_to']} <@{bot_ids[BOT_CFG_FLAG]['tipcc']}>.\n\n<@{bot_ids[BOT_CFG_FLAG]['tipcc']}> {locale_msg[lang]['does_not_support_tips']} <@{bot_ids[BOT_CFG_FLAG]['uttcex']}>."
            await ereply(p[0], e)
            return
        case (12):  # Exchange disabled
            e.description = f"{locale_msg[lang]['exchange_disabled']}"
            await ereply(p[0], e)
            return
        case (13):  # Decimals not allowed in atomic amounts
            e.description = f"{locale_msg[lang]['no_dec_in_atom']}"
            await ereply(p[0], e)
        case (14):  # Some financial deposit feature is disabled, always: view = None
            e.description = p[1]
            await p[0].reply(embed=e, view=None)
            return
        case (15):  # Too many members for tip rain
            e.description = f"{locale_msg[lang]['too_many_tip_rain']} `20`."
            await ereply(p[0], e)
            return
        case (16):  # Amount too small
            e.description = f"{locale_msg[lang]['amount_too_small']}"
            await ereply(p[0], e)
            return
        case (17):  # Invalid coin
            e.description = f"{locale_msg[lang]['coin_not_supported']}"
            await ereply(p[0], e)
            return
        case (18):  # Too few members for tip rain
            e.description = f"The minimum for rain is `2`."
            await ereply(p[0], e)
            return
        case (19):  # Do not swap this way
            e.description = f"To swap, use `u.swap`"
            await ereply(p[0], e)
            return
        case _:
            return


### ERROR ###


### DISCORD REPLY ###
async def reply(msg: discord.Message, r: str):
    await msg.reply(r)
    return


async def ereply(msg: discord.Message, e: discord.Embed):
    await msg.reply(embed=e)
    return


### DISCORD REPLY ###


### DISCORD DO COMMAND ###
async def do_cmd(cmd: str, msg: discord.Message):
    lang = None
    try:
        lang = profile_locale[
            (await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(msg.author.id)))[2]]
    except:
        lang = profile_locale["0"]
    msg.content = await sanistr(msg.content)
    # Helps
    if cmd == "help":
        await basic_help(msg)
        return
    if cmd == "swaphelp":
        await swap_help(msg)
        return
    if cmd == "stakehelp":
        await stake_help(msg)
        return
    if cmd == "escrowhelp":
        await escrow_help(msg)
        return
    if cmd == "bathelp":
        await autotrade_help(msg)
        return
    if cmd == "fafhelp":
        await autotrade_help(msg)
        return
    if cmd == "confighelp":
        await config_help(msg)
        return
    # Basics
    elif cmd == "commands":
        await commands(msg)
        return
    elif cmd == "status":
        await status(msg)
        return
    elif cmd == "time":
        await get_time(msg)
        return
    elif cmd == "ping":
        await ping(msg)
        return
    elif cmd == "locale":
        await set_locale(msg)
        return
    elif cmd == "profile":
        await profile(msg)
        return
    elif cmd == "privacy":
        await privacy(msg)
        return
    elif cmd == "rank":
        await rank(msg)
        return
    elif cmd == "ranks":
        await ranks(msg)
        return
    elif cmd == "servers":
        await server_list(msg)
        return
    elif cmd == "about":
        await about(msg)
        return
    elif cmd == "version":
        await version(msg)
        return
    elif cmd == "how2earn":
        await how_to_earn(msg)
        return
    elif cmd == "friend":
        await friend(msg)
        return
    elif cmd == "unfriend":
        await unfriend(msg)
        return
    elif cmd == "mail":
        await mail(msg)
        return
    elif cmd == "support":
        await support(msg)
        return
    # Wallet
    elif cmd == "price":
        await show_price(msg)
        return
    elif cmd == "convert":
        await convert(msg)
        return
    elif cmd == "coins":
        await show_coin_list(msg)
        return
    elif cmd == "rate":
        await show_rate(msg)
        return
    elif ((cmd == "tip") or (cmd == "send")):
        await tipsend(msg)
        return
    elif cmd == "airdrop":
        await airdrop(msg)
        return
    elif cmd == "bal":
        await balance(msg)
        return
    elif cmd == "bals":
        await balances(msg)
        return
    elif cmd == "swapbal":
        await swap_balance(msg)
        return
    elif ((cmd == "deposit") or (cmd == "dep")):
        await deposit(msg)
        return
    elif cmd == "withdraw":
        await withdraw(msg)
        return
    elif cmd == "escrow":
        await escrow(msg)
        return
    elif cmd == "testswap":
        await testswap(msg)
        return
    elif cmd == "swap":
        await swap(msg)
        return
    # Advanced Commands
    elif cmd == "netlink":
        await netlink(msg)
        return
    elif cmd == "whitelist":
        await whitelistcmd(msg)
        return
    # Host Commands
    elif cmd == "config":
        await config(msg)
        return
    elif cmd == "stafflist":
        await stafflist(msg)
        return
    elif cmd == "purge":
        await purge(msg)
        return
    # Admins
    elif cmd == "say":
        await say(msg)
        return
    elif cmd == "setstaff":
        await set_staff(msg)
        return
    elif cmd == "removestaff":
        await remove_staff(msg)
        return
    elif cmd == "setauth":
        await set_auth(msg)
        return
    elif cmd == "setlevel":
        await set_level(msg)
        return
    elif cmd == "u_ban":
        await u_ban(msg)
        return
    elif cmd == "u_unban":
        await u_unban(msg)
        return
    elif cmd == "enable":
        await u_enable(msg)
        return
    elif cmd == "disable":
        await u_disable(msg)
        return
    elif cmd == "restart":
        u_restart()
        return
    elif cmd == "update_banlist":
        await update_uttcex_bans(msg)
        return
    elif cmd == "credit":
        await credit(msg)
        return
    elif cmd == "mass_credit":
        await mass_credit(msg)
        return
    elif cmd == "mass_debit":
        await mass_debit(msg)
        return
    elif cmd == "debit":
        await debit(msg)
        return
    elif cmd == "dump":
        await dump(msg)
        return
    elif cmd == "webadmin2fa":
        await webadmin2fa(msg)
        return
    elif cmd == "depcredit":
        await depcredit(msg)
        return
    elif cmd == "noreply":
        await noreply(msg)
        return
    elif cmd == "isnoreply":
        await isnoreply(msg)
        return
    elif cmd == "announce":
        await announce(msg)
        return
    # Tests
    elif cmd == "authtest":
        await auth_test(msg)
        return
    elif cmd == "discrepancy":
        await discrepancy(msg)
        return
    elif cmd == "gmfc":
        await grabmsgsfromch(msg)
        return
    elif cmd == "import_banlist":
        await import_banlist(msg)
        return
    elif cmd == "check_bal":
        await check_bal(msg)
        return
    else:
        e = discord.Embed(title=f"{locale_msg[lang]['temporary_message']}",
                          description=f"{locale_msg[lang]['temporary_message_msg']}", color=0xffffff)
        await ereply(msg, e)
        return


async def dm(tid, content: str):
    user = client.get_user(tid)
    await user.send(content)
    return


async def edm(tid, e: discord.Embed):
    user = client.get_user(int(tid))
    try:
        await user.send(embed=e)
    except:
        return
    return


### DISCORD DO COMMAND ###


### SQL WRAPPER ###
## Must use
#
# conn.commit()
#
# before
#
# conn.close()     -- Must always call this.
#
#
#
#
# for DB write operations
##
sql_connected = False

async def sql_conn(db: str):
    global sql_connected
    sql_connected = True
    while (sql_connected == True):
        try:
            conn = mysql.connector.connect(host="localhost",
                                           user="UTTCex",
                                           password=os.getenv("SQL_DB_PASS"),
                                           database=db)
            sql_connected = False
        except mysql.connector.errors.ProgrammingError as e:
            await gprint(f"Failed to connect to SQL database.\n{e}\nRetrying in 1 second...\n", "botright", "log")
            time.sleep(1)
        except mysql.connector.errors.InterfaceError as e:
            await gprint(f"Failed to connect to SQL database.\n{e}\nRetrying in 1 second...\n", "botright", "log")
            time.sleep(1)
    return conn

def t_sql_conn(db: str):
    global sql_connected
    sql_connected = True
    while (sql_connected == True):
        try:
            conn = mysql.connector.connect(host="localhost",
                                           user="UTTCex",
                                           password=os.getenv("SQL_DB_PASS"),
                                           database=db)
            sql_connected = False
        except mysql.connector.errors.ProgrammingError as e:
            t_gprint(f"Failed to connect to SQL database.\n{e}\nRetrying in 1 second...\n", "botright", "log")
            time.sleep(1)
        except mysql.connector.errors.InterfaceError as e:
            t_gprint(f"Failed to connect to SQL database.\n{e}\nRetrying in 1 second...\n", "botright", "log")
            time.sleep(1)
    return conn


async def sql_update(db: str, table: str, col: str, nval: str, scol: str, sval: str):
    """
    UPDATE <table> SET <col> WHERE <row> = <value>
    await sql_update(db, table, col, nval, scol, sval)

    Automatically determines the type of <value>
    But must be either int, float, or str
    """
    conn = await sql_conn(db)
    stmt = conn.cursor(prepared=True)
    if sval == "*":
        stmt.execute(f"UPDATE `{table}` SET `{col}` = '{nval}' WHERE `{scol}` = `{scol}`;")
    else:
        stmt.execute(f"UPDATE `{table}` SET `{col}` = '{nval}' WHERE `{scol}` = '{sval}';")
    conn.commit()
    conn.close()
    return


def t_sql_update(db: str, table: str, col: str, nval: str, scol: str, sval: str):
    """
    UPDATE <table> SET <col> WHERE <row> = <value>
    t_sql_update(db, table, col, nval, scol, sval)

    <value> must always be type str
    """
    conn = t_sql_conn(db)
    stmt = conn.cursor(prepared=True)
    if sval == "*":
        stmt.execute(f"UPDATE `{table}` SET `{col}` = '{nval}' WHERE `{scol}` = `{scol}`;")
    else:
        stmt.execute(f"UPDATE `{table}` SET `{col}` = '{nval}' WHERE `{scol}` = '{sval}';")
    conn.commit()
    conn.close()
    return


async def sql_select(db: str, table: str, col: str, value: str):
    """
    SELECT * FROM <table> WHERE <col> = <value>
    x = await sql_select(db, table, col, value)

    <value> must always be type str
    """
    while (True):
        try:
            conn = await sql_conn(db)
            break
        except:
            continue
    stmt = conn.cursor(prepared=True)
    if col == "*" and value == "*":
        stmt.execute(f"SELECT * FROM `{table}`;")
        result = stmt.fetchall()
        if len(result) == 0:
            conn.close()
            return None
        conn.close()
        return [[bytearray(x[y]).decode("utf-8") for y in range(len(x))] for x in result]
    elif value == "*":
        stmt.execute(f"SELECT `{col}` FROM `{table}`;")
        result = stmt.fetchall()
        if len(result) == 0:
            conn.close()
            return None
        conn.close()
        return [bytearray(x[0]).decode('utf-8') for x in result]
    else:
        stmt.execute(f"SELECT * FROM `{table}` WHERE `{col}` = '{value}';")
        result = stmt.fetchall()
        if len(result) == 0:
            conn.close()
            return None
        conn.close()
        return [bytearray(x).decode('utf-8') for x in result[0]]


def t_sql_select(db: str, table: str, col: str, value: str):
    """
    SELECT * FROM <table> WHERE <col> = <value>
    x = t_sql_select(db, table, col, value)

    <value> must always be type str
    """
    while (True):
        try:
            conn = t_sql_conn(db)
            break
        except:
            continue
    stmt = conn.cursor(prepared=True)
    if col == "*" and value == "*":
        stmt.execute(f"SELECT * FROM `{table}`;")
        result = stmt.fetchall()
        if len(result) == 0:
            conn.close()
            return None
        conn.close()
        return [[bytearray(x[y]).decode('utf-8') for y in range(len(x))] for x in result]
    elif value == "*":
        stmt.execute(f"SELECT `{col}` FROM `{table}`;")
        result = stmt.fetchall()
        if len(result) == 0:
            conn.close()
            return None
        conn.close()
        return [bytearray(x[0]).decode('utf-8') for x in result]
    else:
        stmt.execute(f"SELECT * FROM `{table}` WHERE `{col}` = '{value}';")
    result = stmt.fetchall()
    if len(result) == 0:
        sql_shared = None
        conn.close()
        return
    conn.close()
    return [bytearray(x).decode() for x in result[0]]


async def sql_insert(db: str, table: str, col: str, value: str):
    """
    INSERT INTO <table> (<col>) VALUES (<value>)
    await sql_insert(db, table, col, value)

    <value> must always be type str
    """
    conn = await sql_conn(db)
    stmt = conn.cursor(prepared=True)
    stmt.execute(f"INSERT INTO `{table}` (`{col}`) VALUES ('{value}');")
    conn.commit()
    conn.close()
    return


def t_sql_insert(db: str, table: str, col: str, value: str):
    """
    INSERT INTO <table> (<col>) VALUES (<value>)
    t_sql_insert(db, table, col, value)

    <value> must always be type str
    """
    conn = t_sql_conn(db)
    stmt = conn.cursor(prepared=True)
    stmt.execute(f"INSERT INTO `{table}` (`{col}`) VALUES ('{value}');")
    conn.commit()
    conn.close()
    return


async def sql_delete(db: str, table: str, col: str, value: str):
    conn = t_sql_conn(db)
    stmt = conn.cursor(prepared=True)
    stmt.execute(f"DELETE FROM `{table}` WHERE `{col}` = '{value}';")
    conn.commit()
    conn.close()
    return


def t_sql_delete(db: str, table: str, col: str, value: str):
    conn = t_sql_conn(db)
    stmt = conn.cursor(prepared=True)
    stmt.execute(f"DELETE FROM `{table}` WHERE `{col}` = '{value}';")
    conn.commit()
    conn.close()
    return


async def sql_do(db: str, cmd: str):
    conn = await sql_conn(db)
    stmt = conn.cursor(prepared=True)
    stmt.execute(cmd)
    conn.commit()
    conn.close()
    return


def t_sql_do(db: str, cmd: str):
    conn = t_sql_conn(db)
    stmt = conn.cursor(prepared=True)
    stmt.execute(cmd)
    conn.commit()
    conn.close()
    return


### SQL WRAPPER ###


##### COMMANDS #####
# Helps #
async def basic_help(msg: discord.Message):
    await msg.reply(embed = e_basichelp)
    return


async def swap_help(msg: discord.Message):
    await msg.reply(embed = e_swaphelp)
    return


async def stake_help(msg: discord.Message):
    await msg.reply(embed = e_stakehelp)
    return


async def escrow_help(msg: discord.Message):
    await msg.reply(embed = e_escrowhelp)
    return


async def autotrade_help(msg: discord.Message):
    await msg.reply(embed = e_autotrade_help)
    return


async def config_help(msg: discord.Message):
    await msg.reply(embed = e_config_help)
    return

# Basics #

# --- MENU STUFF --- #
options_list = {"commands": 0,
                "deposit": 1,
                "swap": 2,
                "coinswap": 3,
                "locale": 99}

lang_emoji = {"English": "🇺🇸",
              "Deutsch": "🇩🇪",
              "Español": "🇲🇽",
              "Français": "🇫🇷",
              "Italiano": "🇮🇹",
              "Polski": "🇵🇱",
              "Русский": "🇷🇺",
              "Српски": "🇷🇸",
              "Română": "🇷🇴",
              "Ελληνικά": "🇬🇷",
              "中國人": "🇨🇳",
              "日本語": "🇯🇵",
              "한국인": "🇰🇷",
              "Türkçe": "🇹🇷"
              }


async def do_callback(menu: discord.ui.Select, interaction: discord.Interaction, switch: int) -> discord.ui.Select:
    global atomnames
    mx = interaction.message
    lang = profile_locale[(await sql_select("uttcex_bot_db", "profiles", "discord_id", interaction.user.id))[2]]
    cdata = menu.cdata
    origin = str(interaction.user.id)
    coin = list(cdata.split(" "))[0]
    amount = None
    try:
        amount = list(cdata.split(" "))[1]
    except:
        pass
    match (switch):
        case (0):  # Commands Menu
            footer = locale_msg[lang]['commands_footer']
            page = [
                f"**{locale_msg[lang]['cmds_important_commands']}:**\n```\nu.commands\nu.status\nu.time\nu.locale\nu.how2earn\nu.about```\n**{locale_msg[lang]['cmds_wallet_commands']}:**```\nu.deposit\nu.withdraw\nu.bal```\n**{locale_msg[lang]['cmds_crypto_commands']}:**```\nu.send\nu.tip\nu.airdrop\nu.price```\n**{locale_msg[lang]['cmds_user_commands']}:**\n```\nu.profile\nu.privacy\nu.rank\nu.ranks\nu.level```",
                f"**{locale_msg[lang]['cmds_advanced_commands']}:**",
                f"**{locale_msg[lang]['cmds_user_moderation']}:**\n```\n[u.mute] [u.unmute]\nu.kick\n[u.ban] [u.unban]```\n**{locale_msg[lang]['cmds_channel_moderation']}:**\n```\n[u.lock] [u.unlock]\nu.purge```",
                f"**{locale_msg[lang]['cmds_host_commands']}:**\n```\nu.config```"
                ]
            if (menu.values[0] == "1"):
                if (menu.responded == False):
                    menu.responded = True
                    e = discord.Embed(title=f"{locale_msg[lang]['cmds_basic_commands']}", description=f"{page[0]}",
                                      color=0xffffff)
                    e.set_footer(text=footer)
                    await mx.edit(embed=e, view=None)
                    return menu
                else:
                    return menu
            elif menu.values[0] == "2":
                if (menu.responded == False):
                    menu.responded = True
                    e = discord.Embed(title=f"{locale_msg[lang]['cmds_advanced_commands']}", description=f"{page[1]}",
                                      color=0xffffff)
                    e.set_footer(text=footer)
                    await mx.edit(embed=e, view=None)
                    return menu
                else:
                    return menu
            elif menu.values[0] == "3":
                if (menu.responded == False):
                    menu.responded = True
                    e = discord.Embed(title=f"{locale_msg[lang]['cmds_moderation_commands']}", description=f"{page[2]}",
                                      color=0xffffff)
                    e.set_footer(text=footer)
                    await mx.edit(embed=e, view=None)
                    return menu
                else:
                    return menu
            elif menu.values[0] == "4":
                if (menu.responded == False):
                    menu.responded = True
                    e = discord.Embed(title=f"{locale_msg[lang]['cmds_host_commands']}", description=f"{page[3]}",
                                      color=0xffffff)
                    e.set_footer(text=footer)
                    await mx.edit(embed=e, view=None)
                    return menu
                else:
                    return menu
        case (1):  # Deposit Menu
            amount = list(cdata.split(" "))[1]
            coin = list(cdata.split(" "))[0]
            footer = "Deposits will deduct from your account.\nDeposits will remain active until completed or cancelled."
            page = [
                "Swapping is as simple as following the menus. Just select what you want and your coins will automatically trade in your account.\n\nIf you have your profile privacy turned on, your balance will be sent to you via DM.",
                "### **Staking with UTTCex:**\n\nYour coins will go into that coin's staking pool.\nYou can withdraw at any time.\nEarly withdrawal will result in a **0.5%** fee.\nYou can enable or disable restaking on your deposit.\nIf you stake more of the same coin, it is added to your original stake.\n\nThe amount you earn is directly proportional to the percent of the pool you own.\nIf you own 10% of the pool, you get 10% of the stake rewards generated.\n\nStake rewards are generated from swap fees. **25%** of every swap fee goes to the pool of the coin the fee was collected in.\nYour % ownership of the pool is the % of this fee that you earn.",
                "Escrow",
                "Loan",
                "Auto Trade"]
            if (menu.values[0] == "1"):
                if (menu.responded == False):
                    menu.responded = True
                    e = discord.Embed(title="Swap Menu", description=f"{page[0]}", color=0xffffff)
                    e.set_footer(
                        text=f"You can DM UTTCex commands like u.tip along with their Discord ID to tip someone anonymously.")
                    e.set_footer(text=footer)
                    if (exenabled == True):
                        await mx.edit(embed=e, view=SwapMenu(cdata))
                    else:
                        await err(-1, [mx,
                                       f"The Exchange is currently disabled. Please wait for an update or try later.\n\n{footer}"])
                        return menu
                else:
                    return menu
            elif (menu.values[0] == "2"):
                if (menu.responded == False):
                    menu.responded = True
                    e = discord.Embed(title="Staking Menu", description=f"{page[1]}", color=0xffffff)
                    e.set_footer(
                        text=f"You can DM UTTCex commands like u.tip along with their Discord ID to tip someone anonymously.")
                    e.set_footer(text=footer)
                    if (exenabled == True):
                        await mx.edit(embed=e, view=None)
                        return menu
                    else:
                        await err(14, [mx,
                                       f"Staking is currently disabled. Please wait for an update or try later.\n\n{footer}"])
                        return menu
                else:
                    return menu
            elif (menu.values[0] == "3"): # Escrow deposit via user >> uttcex tip
                # # --- deprecated, use u.escrow instead
                if (menu.responded == False):
                    menu.responded = True
                    data = await sql_select("uttcex_bot_db", "escrows", "origin", origin)
                    if (data == None):
                        data = await sql_select("uttcex_bot_db", "escrows", "target", origin)
                        if (data == None):
                            e = discord.Embed(title="Error",
                                              description="You are not engaged in escrow and have nowhere to deposit.",
                                              color=0xff0000)
                            await mx.edit(embed=e, view=None)
                            return
                    eid = data[2]
                    if (coin in atomnames):  # This is an atomic tip
                        coin = alias[coin]
                        amount = format(await from_atomic(coin, amount), decidic[coin])
                    else:
                        amount = format(Decimal(amount), decidic[coin])
                    cdata = f"{origin}_{coin}"
                    await sql_do("uttcex_escrows",
                                 f"INSERT INTO `{eid}` (`coin`, `amount`) VALUES ('{cdata}','{amount}')")
                    e = discord.Embed(title="Escrow", description=f"You have deposited **{amount}** {emojis[coin]}",
                                      color=0xff00ff)
                    e.set_footer(text="Escrow deposits remain active until completed or cancelled.")
                    if (esenabled == True):
                        await mx.edit(embed=e, view=None)
                        return menu
                    else:
                        e = discord.Embed(title="Escrow Disabled",
                                          description="Escrows are currently disabled and are under development.",
                                          color=0xffffff)
                        await mx.edit(embed=e, view=None)
                        return menu
                else:
                    return menu
            elif (menu.values[0] == "4"):
                if (menu.responded == False):
                    menu.responded = True
                    e = discord.Embed(title="Loan Menu", description=f"{page[3]}", color=0xffffff)
                    e.set_footer(text=footer)
                    if (exenabled == True):
                        await mx.edit(embed=e, view=None)
                        return menu
                    else:
                        await err(14, [mx,
                                       f"Loans are currently disabled. Please wait for an update or try later.\n\n{footer}"])
                        return menu
                else:
                    return menu
            elif (menu.values[0] == "5"):
                if (menu.responded == False):
                    menu.responded = True
                    e = discord.Embed(title="Auto Trade Wizard", description=f"{page[4]}", color=0xffffff)
                    e.set_footer(text=footer)
                    if (exenabled == True):
                        await mx.edit(embed=e, view=None)
                        return menu
                    else:
                        await err(14, [mx,
                                       f"Auto Trade is currently disabled. Please wait for an update or try later.\n\n{footer}"])
                        return menu
                else:
                    return menu
            elif (menu.values[0] == "6"):
                if (menu.responded == False):
                    menu.responded = True
                    await unlock_bal(origin, coin, amount)
                    e = discord.Embed(title="Cancelled deposit.", description=f"You have selected to cancel.",
                                      color=0xffffff)
                    e.set_footer(
                        text=f"You can DM UTTCex commands like u.tip along with their Discord ID to tip someone or trade anonymously.\nYou can even escrow from DM!")
                    e.set_footer(text="No money was moved from your account.")
                    await mx.edit(embed=e, view=None)
                    return menu
                else:
                    return menu
        case (2):  # Swaps
            footer = "Deposits are not processed until you finalize your operation.\nYou will not lose crypto if the bot goes offline or you abandon the deposit."
            if (menu.values[0] == "1"):
                if (menu.responded == False):
                    menu.responded = True
                    e = discord.Embed(title="Rates", description=f"**List of coins from 0.99 to 0.95:**",
                                      color=0xffffff)
                    e.set_footer(text=footer)
                    if (exenabled == True):
                        await mx.edit(embed=e, view=CoinSwapMenu(cdata, 1))
                        return menu
                    else:
                        await err(14, [mx,
                                       f"The exchange is currently disabled. Please wait for an update or try later.\n\n{footer}"])
                        return menu
                else:
                    return menu
            elif (menu.values[0] == "2"):
                if (menu.responded == False):
                    menu.responded = True
                    e = discord.Embed(title="Rates", description=f"**List of coins from 0.94 to 0.90:**",
                                      color=0xffffff)
                    e.set_footer(text=footer)
                    if (exenabled == True):
                        await mx.edit(embed=e, view=CoinSwapMenu(cdata, 2))
                        return menu
                    else:
                        await err(14, [mx,
                                       f"The exchange is currently disabled. Please wait for an update or try later.\n\n{footer}"])
                        return menu
                else:
                    return menu
            elif (menu.values[0] == "3"):
                if (menu.responded == False):
                    menu.responded = True
                    await unlock_bal(origin, coin, amount)
                    e = discord.Embed(title="Cancelled swap.",
                                      description=f"You have selected to cancel. No money was taken from your account.",
                                      color=0xffffff)
                    e.set_footer(text=footer)
                    if (exenabled == True):
                        await mx.edit(embed=e, view=None)
                        return menu
                    else:
                        await err(14, [mx, f"An error occurred?.\n\n{footer}"])
                        return menu
                else:
                    return menu
        case (3):  # Coin Swap Menu
            if (menu.responded == False):
                menu.responded = True
            else:
                return menu
            await unlock_bal(origin, coin, amount)
            return
        case (99):
            if (menu.values[0] == "1"): # English
                if (menu.responded == False):
                    menu.responded = True
                    await sql_update("uttcex_bot_db", "profiles", "language", "0", "discord_id",
                                     str(interaction.user.id))
                    lang = profile_locale[
                        (await sql_select("uttcex_bot_db", "profiles", "discord_id", interaction.user.id))[2]]
                    footer = locale_msg[lang]['lang_not_displaying_footer']
                    e = discord.Embed(title=f"{lang_emoji[lang]} {locale_msg[lang]['language_set']}",
                                      description=f"{locale_msg[lang]['your_language_is_now']}",
                                      color=0xffffff)
                    e.set_footer(text=footer)
                    await mx.edit(embed=e, view=None)
                    return menu
                else:
                    return menu
            if (menu.values[0] == "2"): # Spanish
                if (menu.responded == False):
                    menu.responded = True
                    await sql_update("uttcex_bot_db", "profiles", "language", "1", "discord_id",
                                     str(interaction.user.id))
                    lang = profile_locale[
                        (await sql_select("uttcex_bot_db", "profiles", "discord_id", interaction.user.id))[2]]
                    footer = locale_msg[lang]['lang_not_displaying_footer']
                    e = discord.Embed(title=f"{lang_emoji[lang]} {locale_msg[lang]['language_set']}",
                                      description=f"{locale_msg[lang]['your_language_is_now']}\n\n{locale_msg[lang]['lang_not_displaying']}",
                                      color=0xffffff)
                    e.set_footer(text=footer)
                    await mx.edit(embed=e, view=None)
                    return menu
                else:
                    return menu
            elif (menu.values[0] == "3"): # German
                if (menu.responded == False):
                    menu.responded = True
                    await sql_update("uttcex_bot_db", "profiles", "language", "2", "discord_id", str(interaction.user.id))
                    lang = profile_locale[
                        (await sql_select("uttcex_bot_db", "profiles", "discord_id", interaction.user.id))[2]]
                    footer = locale_msg[lang]['lang_not_displaying_footer']
                    e = discord.Embed(title=f"{lang_emoji[lang]} {locale_msg[lang]['language_set']}",
                                      description=f"{locale_msg[lang]['your_language_is_now']}\n\n{locale_msg[lang]['lang_not_displaying']}",
                                      color=0xffffff)
                    e.set_footer(text=footer)
                    await mx.edit(embed=e, view=None)
                    return menu
                else:
                    return menu
            elif (menu.values[0] == "0"): # Default
                if (menu.responded == False):
                    menu.responded = True
                    await sql_update("uttcex_bot_db", "profiles", "language", "0", "discord_id",
                                     str(interaction.user.id))
                    lang = profile_locale[
                        (await sql_select("uttcex_bot_db", "profiles", "discord_id", interaction.user.id))[2]]
                    footer = locale_msg[lang]['lang_not_displaying_footer']
                    e = discord.Embed(title=f"{lang_emoji['English']} Default Language Set",
                                      description=f"**Your language is now the default.**", color=0xffffff)
                    e.set_footer(text=footer)
                    await mx.edit(embed=e, view=None)
                    return menu
                else:
                    return menu
            else:
                menu.responded = True
                e = discord.Embed(title = "Unavailable", description="The selected language is not added yet.\nPlease try again later.", color = 0xffffff)
                await mx.edit(embed = e, view = None)
                return menu
        case _:
            return menu


class CommandsMenu(discord.ui.View):
    def __init__(self, lang, timeout=30):
        super().__init__(timeout=timeout)
        self.add_item(CommandsOptions(lang))


class CommandsOptions(discord.ui.Select):
    def __init__(self, lang):
        self.lang = lang
        options = [
            discord.SelectOption(label="1", emoji="1️⃣",
                                 description=f"{locale_msg[self.lang]['cmds_basic_commands']}."),
            discord.SelectOption(label="2", emoji="2️⃣", description=f"{locale_msg[lang]['cmds_advanced_commands']}."),
            discord.SelectOption(label="3", emoji="3️⃣",
                                 description=f"{locale_msg[lang]['cmds_moderation_commands']}."),
            discord.SelectOption(label="4", emoji="4️⃣", description=f"{locale_msg[lang]['cmds_host_commands']}.")
        ]
        self.responded = False
        super().__init__(placeholder=f"{locale_msg[self.lang]['select_an_option']}", max_values=1, min_values=1,
                         options=options)

    async def callback(self, interaction: discord.Interaction):
        await do_callback(self, interaction, options_list["commands"])
        return


class DepositMenu(discord.ui.View):
    def __init__(self, cdata, timeout=30):
        super().__init__(timeout=timeout)
        self.add_item(DepositOptions(cdata))


class DepositOptions(discord.ui.Select):
    def __init__(self, cdata):
        options = [
            discord.SelectOption(label="1", emoji="💸", description="Swap your coins."),
            discord.SelectOption(label="2", emoji="💰", description="Stake your coins."),
            discord.SelectOption(label="3", emoji="↔️", description="Escrow this deposit."),
            discord.SelectOption(label="4", emoji="💎", description="Get a crypto loan."),
            discord.SelectOption(label="5", emoji="🔥", description="Auto Trade this deposit."),
            discord.SelectOption(label="6", emoji="❌", description="Cancel")
        ]
        self.responded = False
        self.cdata = cdata
        super().__init__(placeholder="Select an Option", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await do_callback(self, interaction, options_list["deposit"])
        return


class SwapMenu(discord.ui.View):
    def __init__(self, cdata, timeout=30):
        super().__init__(timeout=timeout)
        self.add_item(SwapOptions(cdata))


class SwapOptions(discord.ui.Select):
    def __init__(self, cdata):
        options = [
            discord.SelectOption(label="1", emoji="💸", description="Rates (0.99 to 0.95)"),
            discord.SelectOption(label="2", emoji="💸", description="Rates (0.94 to 0.90)"),
            discord.SelectOption(label="3", emoji="❌", description="Cancel")
        ]
        self.responded = False
        self.cdata = cdata
        super().__init__(placeholder="Select an Option", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await do_callback(self, interaction, options_list["swap"])
        return


class CoinSwapMenu(discord.ui.View):
    def __init__(self, cdata, which, timeout=30):
        super().__init__(timeout=timeout)
        self.add_item(CoinSwapOptions(cdata, which))


class CoinSwapOptions(discord.ui.Select):
    def __init__(self, cdata, which: int):
        match (which):
            case (1):
                self.options = [
                    discord.SelectOption(label="1", emoji=f"{emojis['btc']}", description=f"Rate: {rate_dic['btc']}"),
                    discord.SelectOption(label="2", emoji=f"{emojis['ltc']}", description=f"Rate: {rate_dic['ltc']}"),
                    discord.SelectOption(label="3", emoji=f"{emojis['doge']}", description=f"Rate: {rate_dic['doge']}"),
                    discord.SelectOption(label="4", emoji=f"{emojis['eth']}", description=f"Rate: {rate_dic['eth']}"),
                    discord.SelectOption(label="5", emoji=f"{emojis['usdc']}", description=f"Rate: {rate_dic['usdc']}"),
                    discord.SelectOption(label="6", emoji=f"{emojis['usdt']}", description=f"Rate: {rate_dic['usdt']}"),
                    discord.SelectOption(label="7", emoji=f"{emojis['shib']}", description=f"Rate: {rate_dic['shib']}"),
                    discord.SelectOption(label="8", emoji=f"{emojis['matic']}",
                                         description=f"Rate: {rate_dic['matic']}"),
                    discord.SelectOption(label="9", emoji=f"{emojis['bnb']}", description=f"Rate: {rate_dic['bnb']}"),
                    discord.SelectOption(label="10", emoji=f"{emojis['busd']}",
                                         description=f"Rate: {rate_dic['busd']}"),
                    discord.SelectOption(label="11", emoji=f"{emojis['cds']}", description=f"Rate: {rate_dic['cds']}"),
                    discord.SelectOption(label="12", emoji=f"{emojis['op']}", description=f"Rate: {rate_dic['op']}"),
                    discord.SelectOption(label="13", emoji=f"{emojis['avax']}",
                                         description=f"Rate: {rate_dic['avax']}"),
                    discord.SelectOption(label="14", emoji=f"{emojis['xrp']}", description=f"Rate: {rate_dic['xrp']}"),
                    discord.SelectOption(label="15", emoji="❌", description="Cancel")
                ]
            case (2):
                self.options = [
                    discord.SelectOption(label="1", emoji=f"{emojis['pussy']}",
                                         description=f"Rate: {rate_dic['pussy']}"),
                    discord.SelectOption(label="15", emoji="❌", description="Cancel")
                ]
        self.responded = False
        self.cdata = cdata
        super().__init__(placeholder="Select an Option", max_values=1, min_values=1, options=self.options)

    async def callback(self, interaction: discord.Interaction):
        await do_callback(self, interaction, options_list["swap"])
        return


class LocaleMenu(discord.ui.View):
    def __init__(self, *, timeout=30):
        super().__init__(timeout=timeout)
        self.add_item(LocaleOptions())


class LocaleOptions(discord.ui.Select):
    def __init__(self):
        options = [
            # Descriptions need to be translated as well.
            discord.SelectOption(label="1", emoji=lang_emoji["English"], description="Select English"),
            discord.SelectOption(label="2", emoji=lang_emoji["Deutsch"], description="Select German"),
            discord.SelectOption(label="3", emoji=lang_emoji["Español"], description="Select Español"),
            discord.SelectOption(label="4", emoji=lang_emoji["Français"], description="Select French"),
            discord.SelectOption(label="5", emoji=lang_emoji["Italiano"], description="Select Italian"),
            discord.SelectOption(label="6", emoji=lang_emoji["Polski"], description="Select Polish"),
            discord.SelectOption(label="7", emoji=lang_emoji["Русский"], description="Select Russian"),
            discord.SelectOption(label="8", emoji=lang_emoji["Српски"], description="Select Serbian"),
            discord.SelectOption(label="9", emoji=lang_emoji["Română"], description="Select Romanian"),
            discord.SelectOption(label="10", emoji=lang_emoji["Ελληνικά"], description="Select Greek"),
            discord.SelectOption(label="11", emoji=lang_emoji["中國人"], description="Select Chinese"),
            discord.SelectOption(label="12", emoji=lang_emoji["日本語"], description="Select Japanese"),
            discord.SelectOption(label="13", emoji=lang_emoji["한국인"], description="Select Korean"),
            discord.SelectOption(label="14", emoji=lang_emoji["Türkçe"], description="Select Turkish"),
            discord.SelectOption(label="0", emoji=lang_emoji["English"], description="Default English")
        ]
        self.responded = False
        self.cdata = ""
        super().__init__(placeholder="Select an Option", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await do_callback(self, interaction, options_list["locale"])
        return


# --- MENU STUFF --- #


async def commands(msg: discord.Message):
    lang = profile_locale[
        (await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(msg.author.id)))[2]]
    epc = 0
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    basic = f"**{locale_msg[lang]['cmds_important_commands']}:**\n```\nu.commands\nu.status\nu.time\nu.locale\nu.how2earn\nu.about\nu.version\nu.support```\n**{locale_msg[lang]['cmds_wallet_commands']}:**```\nu.deposit\nu.withdraw\nu.bal```\n**{locale_msg[lang]['cmds_crypto_commands']}:**```\nu.tip | u.send\nu.airdrop\nu.price\nu.swap\nu.stake\nu.escrow\nu.loan\nu.airdrop\nu.price\nu.convert```\n**{locale_msg[lang]['cmds_user_commands']}:**\n```\nu.profile\nu.privacy\nu.rank\nu.ranks\nu.level```"
    advanced = f"**{locale_msg[lang]['cmds_advanced_commands']}:**"
    moderation = f"**{locale_msg[lang]['cmds_user_moderation']}:**\n```\n[u.mute] [u.unmute]\nu.kick\n[u.ban] [u.unban]```\n**{locale_msg[lang]['cmds_channel_moderation']}:**\n```\n[u.lock] [u.unlock]\nu.purge```"
    host = f"**{locale_msg[lang]['cmds_host_commands']}:**\n```\nu.config\nu.setstaff\nu.removestaff```"
    match (len(p)):
        case (1):
            # Show help
            e = discord.Embed(title=f"{locale_msg[lang]['usage_and_commands']}",
                              description=f"{locale_msg[lang]['u_a_c_description1']}{locale_msg[lang]['u_a_c_description2']}{locale_msg[lang]['u_a_c_description3']}",
                              color=0xffffff)
            await ereply(msg, e)
            return
        case (2):
            match (p[1].lower()):
                case ("basic"):
                    e = discord.Embed(title="Basic and Important Commands", description=basic, color=0xffffff)
                    await ereply(msg, e)
                    return
                case ("advanced"):
                    e = discord.Embed(title="Advanced UTTCex Commands", description=advanced, color=0xffffff)
                    await ereply(msg, e)
                    return
                case ("moderation"):
                    e = discord.Embed(title="Server, Channel, and User Moderation", description=moderation,
                                      color=0xffffff)
                    await ereply(msg, e)
                    return
                case ("host"):
                    e = discord.Embed(title="UTTCex Host Commands", description=host, color=0xffffff)
                    await ereply(msg, e)
                    return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def status(msg: discord.Message):
    statuses = await sql_select("uttcex_bot_db", "uttcex_status", "row_id", "0")
    bot_status = []
    for x in statuses:
        bot_status.append(int(x))
    epc = 0
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (1):
            e = discord.Embed(title="UTTCex Discord Status",
                              description=f"Swapping: {await status_flag(bool(bot_status[0]))}\nStaking: {await status_flag(bool(bot_status[1]))} | 🔂 In-Development\nEscrow: {await status_flag(bool(bot_status[2]))}\nLoans: {await status_flag(bool(bot_status[3]))} | 🔂 In-Development\nAuto-Trade: {await status_flag(bool(bot_status[4]))}\nAffiliate Rewards: ✅ Enabled\nWallets: {await status_flag(bool(bot_status[5]))}\nWallet Deposits: {await status_flag(True)}\nFeature Deposits: {await status_flag(bool(bot_status[7]))}",
                              color=0xffffff)
            await ereply(msg, e)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def get_time(msg: discord.Message):
    epc = 0
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (1):
            t = await timestamp()
            e = discord.Embed(title="UTTCex Server Time",
                              description=f"**{t}**\n\nTime is displayed in 24-hour format.\n\nServer Time Zone:\nCentral Time (UTC-4:00H)",
                              color=0xffffff)
            await ereply(msg, e)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def ping(msg: discord.Message):
    epc = 0
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case _:
            await msg.reply(f"Pong! Time: {time.time()}")
            return

async def set_locale(msg: discord.Message):
    epc = 0
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (1):
            await msg.reply(view=LocaleMenu())
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


rank_emojis = {"noob": "⚠",
               "regular": "🔰",
               "experienced": "⚛",
               "uttc_badass": "⚜",
               "guardian": "✳",
               "secret_tourist": "🕵",
               "adventurer": "🚀",
               "grand_adventurer": "🛸",
               "deep_space_pirate": "👽",
               "dominator": emojis["uttc"],
               }


async def get_rank_str(tid) -> list:
    """
    Returns a profile's rank as string and level as int.
    [str,int]
    """
    level = int((await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(tid)))[12])
    if (level <= 10):
        return ["⚠️ Noob", level]
    elif (level <= 15) and (level > 10):
        return ["🔰 Regular", level]
    elif (level <= 20) and (level > 15):
        return ["⚛️ Experienced", level]
    elif (level <= 25) and (level > 20):
        return ["⚜️ UTTC Badass", level]
    elif (level <= 30) and (level > 25):
        return ["✳️ Guardian", level]
    elif (level <= 35) and (level > 30):
        return ["🕵 Secret Tourist", level]
    elif (level <= 40) and (level > 35):
        return ["🚀 Adventurer", level]
    elif (level <= 45) and (level > 40):
        return ["🛸 Grand Adventurer", level]
    elif (level <= 50) and (level > 45):
        return ["👽 Deep-Space Pirate", level]
    elif (level > 50):
        return [f"{emojis['uttc']} Dominator", level]


async def profile(msg: discord.Message):
    footer = "Your UTTCex ID is also your Referral ID"
    tmp = msg.content.lower()
    t = list(tmp.split(" "))
    match (len(t)):
        case 2: # Display another's profile
            if t[1] == "?":
                e = Embed(title = "Extended help, profiles:",
                          description = "",
                          color = 0xffffff)
                await msg.reply(embed = e)
                return
            tid = await udefs.udefs.stripid(t[1])
            if (await ddefs.ddefs.hasprofile(tid)) is True:
                pass # Sanity check
            data = await usql.usql.sql_select("uttcex_bot_db", "profiles", "discord_id", str(tid))
            user = ddefs.client.get_user(tid)
            match (await udefs.udefs.is_banned(tid)):
                case 1:
                    data = await usql.usql.sql_select("uttcex_bot_db", "profiles", "discord_id", str(tid))
                    if data[17] == "":
                        data[17] = "None given."
                    e = Embed(title = "❌ BANNED ❌",
                              description = f"<@{tid}>\n\nThis account was permanently banned for:\n```ansi\n\u001b[0;40;31m{data[16]}\u001b[0;0m```\n**Additional Information:**\n{data[17]}",
                              color = 0xff0000)
                    e.set_footer(text = "Do not interact with this user for any reason.\nThis user cannot send or receive tips, or use UTTCex at all.")
                    e.set_thumbnail(url="https://cdn.discordapp.com/attachments/987754157756780574/1162250849704230922/403_avatar.gif")
                    await msg.reply(embed = e)
                    return
                case 0:
                    pass
            is_private = await udefs.udefs.privacy_flag(tid)
            match is_private:
                case 1:
                    if int(data[1]) > 3:
                        pass
                    else:
                        e = Embed(title = "Error",
                                  description = "This profile is private.",
                                  color = 0xff0000)
                        await msg.reply(embed = e)
                        return
                case 0:
                    pass
            friends = await are_they_friends(msg.author.id, int(tid))
            friendstatus = ""
            if friends is True:
                friendstatus = "\n\nYou and this user are friends!"
            e = Embed(title = f"Profile Viewer",
                      description = f"> **Level: {data[12]}\n> Rank: TODO\n> UTTCex ID: `{data[14]}`**\n\n**Stats:**\n> Total trades: **{data[4]}**\n> Total traded: **${data[5]}**\n> Total escrows: **{data[6]}**\n> Total escrowed: **${data[7]}**\n> Total stakes: **{data[8]}**\n> Total staked: **${data[9]}**\n> Total loans: **{data[10]}**\n> Total loaned: **{data[11]}**" + friendstatus,
                      color = 0xffffff)
            if int(data[1]) > 3:
                e.description += "\n\n> This user is UTTCex staff.\n> Staff profiles are **always** public."
            await msg.reply(embed = e)
            return
        case _: # Display self profile
            tid = msg.author.id
            if (await ddefs.ddefs.hasprofile(tid)) is True:
                pass # Sanity check
            data = await usql.usql.sql_select("uttcex_bot_db", "profiles", "discord_id", str(msg.author.id))
            user = ddefs.client.get_user(tid)
            match (await udefs.udefs.is_banned(tid)):
                case 1:
                    data = await usql.usql.sql_select("uttcex_bot_db", "profiles", "discord_id", str(tid))
                    if data[17] == "":
                        data[17] = "None given."
                    e = Embed(title = "❌ BANNED ❌",
                              description = f"<@{tid}>\n\nThis account was permanently banned for:\n```ansi\n\u001b[0;40;31m{data[16]}\u001b[0;0m```\n**Additional Information:**\n{data[17]}",
                              color = 0xff0000)
                    e.set_footer(text = "Do not interact with this user for any reason.\nThis user cannot send or receive tips, or use UTTCex at all.")
                    e.set_thumbnail(url="https://cdn.discordapp.com/attachments/987754157756780574/1162250849704230922/403_avatar.gif")
                    await msg.reply(embed = e)
                    return
                case 0:
                    pass
            e = Embed(title = "Your Profile",
                      description = f"> **Level: {data[12]}\n> Rank: TODO\n> UTTCex ID: `{data[14]}`**\n\n**Stats:**\n> Total trades: **{data[4]}**\n> Total traded: **${data[5]}**\n> Total escrows: **{data[6]}**\n> Total escrowed: **${data[7]}**\n> Total stakes: **{data[8]}**\n> Total staked: **${data[9]}**\n> Total loans: **{data[10]}**\n> Total loaned: **{data[11]}**",
                      color = 0xffffff)
            if int(data[1]) > 3:
                e.description += "\n\n> This user is UTTCex staff.\n> Staff profiles are **always** public."
            e.set_footer(text=footer)
            await msg.reply(embed = e)
            return


async def privacy(msg: discord.Message):
    epc = 1
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    p[1] = p[1].lower()
    pg = len(p) - 1
    match (len(p)):
        case (1):
            e = discord.Embed(title="Command: u.privacy",
                              description="**Usage:**\n`u.profile` `{state}`\n\n**The `{state}` flag can be:**\n```\non / off\nenabled / disabled\nactive / inactive\ntrue / false```",
                              color=0xffffff)
            await ereply(msg, e)
            return
        case (2):
            if (p[1] == "on") or (p[1] == "enabled") or (p[1] == "enable") or (p[1] == "active") or (p[1] == "true"):
                await sql_update("uttcex_bot_db", "profiles", "privacy", "1", "discord_id",
                                 await stripid(msg.author.id))
                e = discord.Embed(title="Profile is Private", description="✅ **Privacy Enabled**", color=0x00ff00)
                await ereply(msg, e)
                return
            if (p[1] == "off") or (p[1] == "disabled") or (p[1] == "disable") or (p[1] == "inactive") or (p[1] == "false"):
                await sql_update("uttcex_bot_db", "profiles", "privacy", "0", "discord_id",
                                 await stripid(msg.author.id))
                e = discord.Embed(title="Profile is Public", description="❌ **Privacy Disabled**", color=0xff0000)
                await ereply(msg, e)
                return
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


rank_benefits = {"regular": "5% trade fee reduction\nAbility to earn \u001b[1;40;37mCommon Prizes\u001b[0;0m\n",
                 "experienced": "5% trade fee reduction\nAbility to earn \u001b[1;40;37mCommon Prizes\u001b[0;0m\n+5% more received from faucets\nAbility to earn \u001b[1;40;34mUncommon Prizes\u001b[0;0m\n",
                 "uttc_badass": "5% trade fee reduction\nAbility to earn \u001b[1;40;37mCommon Prizes\u001b[0;0m\n+5% more received from faucets\nAbility to earn \u001b[1;40;34mUncommon Prizes\u001b[0;0m\n50% early unstaking period reduction\nAbility to earn \u001b[1;40;33mRare Prizes\u001b[0;0m\n",
                 "guardian": "5% trade fee reduction\nAbility to earn \u001b[1;40;37mCommon Prizes\u001b[0;0m\n+5% more received from faucets\nAbility to earn \u001b[1;40;34mUncommon Prizes\u001b[0;0m\n50% early unstaking period reduction\nAbility to earn \u001b[1;40;33mRare Prizes\u001b[0;0m\n5% trade fee discount\n",
                 "secret_tourist": "5% trade fee reduction\nAbility to earn \u001b[1;40;37mCommon Prizes\u001b[0;0m\n+5% more received from faucets\nAbility to earn \u001b[1;40;34mUncommon Prizes\u001b[0;0m\n50% early unstaking period reduction\nAbility to earn \u001b[1;40;33mRare Prizes\u001b[0;0m\n5% trade fee discount\n4 hour faucet time reduction\nAbility to earn \u001b[1;40;32mUltra Rare Prizes\u001b[0;0m\n",
                 "adventurer": "5% trade fee reduction\nAbility to earn \u001b[1;40;37mCommon Prizes\u001b[0;0m\n+5% more received from faucets\nAbility to earn \u001b[1;40;34mUncommon Prizes\u001b[0;0m\n50% early unstaking period reduction\nAbility to earn \u001b[1;40;33mRare Prizes\u001b[0;0m\n5% trade fee discount\n4 hour faucet time reduction\nAbility to earn \u001b[1;40;32mUltra Rare Prizes\u001b[0;0m\n5% more received from faucets[0;0m\n",
                 "grand_adventurer": "5% trade fee reduction\nAbility to earn \u001b[1;40;37mCommon Prizes\u001b[0;0m\n+5% more received from faucets\nAbility to earn \u001b[1;40;34mUncommon Prizes\u001b[0;0m\n50% early unstaking period reduction\nAbility to earn \u001b[1;40;33mRare Prizes\u001b[0;0m\n5% trade fee discount\n4 hour faucet time reduction\nAbility to earn \u001b[1;40;32mUltra Rare Prizes\u001b[0;0m\n5% more received from faucets\n5% trade fee discount\nAbility to earn \u001b[1;40;35mExtravagant Prizes\u001b[0;0m\n",
                 "deep_space_pirate": "5% trade fee reduction\nAbility to earn \u001b[1;40;37mCommon Prizes\u001b[0;0m\n+5% more received from faucets\nAbility to earn \u001b[1;40;34mUncommon Prizes\u001b[0;0m\n50% early unstaking period reduction\nAbility to earn \u001b[1;40;33mRare Prizes\u001b[0;0m\n5% trade fee discount\n4 hour faucet time reduction\nAbility to earn \u001b[1;40;32mUltra Rare Prizes\u001b[0;0m\n5% more received from faucets\n5% trade fee discount\nAbility to earn \u001b[1;40;35mExtravagant Prizes\u001b[0;0m\n25% early unstaking fee reduction[0;0m\n",
                 "dominator": "5% trade fee reduction\nAbility to earn \u001b[0;40;37mCommon Prizes\u001b[0;0m\n+5% more received from faucets\nAbility to earn \u001b[1;40;34mUncommon Prizes\u001b[0;0m\n50% early unstaking period reduction\nAbility to earn \u001b[1;40;33mRare Prizes\u001b[0;0m\n5% trade fee discount\n4 hour faucet time reduction\nAbility to earn \u001b[1;40;32mUltra Rare Prizes\u001b[0;0m\n5% more received from faucets\n5% trade fee discount\nAbility to earn \u001b[1;40;35mExtravagant Prizes\u001b\u001b[0;0m\n25% early unstaking fee reduction\n5% trade fee discount\nAbility to earn \u001b[0;40;31mSuperior Prizes"}


async def rank(msg):
    epc = 0
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (1):
            if (await has_profile(msg.author.id) == True):
                pass
            data = await sql_select("uttcex_bot_db", "profiles", "discord_id", f"{msg.author.id}")
            level = int(data[16])
            r_str = ""
            e = discord.Embed()
            if (level <= 10):
                e.title = "⚠️ **Noob**"
                r_str = ""
            elif (level <= 15) and (level > 10):
                e.title = "🔰 **Regular**"
                r_str = "```ansi\n{rank_benefits['regular']}```"
            elif (level <= 20) and (level > 15):
                e.title = "⚛️ **Experienced**"
                r_str = "```ansi\n{rank_benefits['experienced']}```"
            elif (level <= 25) and (level > 20):
                e.title = "⚜️ **UTTC Badass**"
                r_str = "```ansi\n{rank_benefits['uttc_badass']}```"
            elif (level <= 30) and (level > 25):
                e.title = "✳️ **Guardian**"
                r_str = "```ansi\n{rank_benefits['guardian']}```"
            elif (level <= 35) and (level > 30):
                e.title = "🕵 **Secret Tourist**"
                r_str = "```ansi\n{rank_benefits['secret_tourist']}```"
            elif (level <= 40) and (level > 35):
                e.title = "🚀 **Adventurer**"
                r_str = "```ansi\n{rank_benefits['adventurer']}```"
            elif (level <= 45) and (level > 40):
                e.title = "🛸 **Grand Adventurer**"
                r_str = "```ansi\n{rank_benefits['grand_adventurer']}```"
            elif (level <= 50) and (level > 45):
                e.title = "👽 **Deep-Space Pirate**"
                r_str = "```ansi\n{rank_benefits['deep_space_pirate']}```"
            elif (level > 50):
                e.title = f"{emojis['uttc']} **Dominator**"
                r_str = f"```ansi\n{rank_benefits['dominator']}```"
            e.description = f"{r_str}\nChat in any server with UTTCex present and you'll earn exp to level up!"
            e.color = 0x762360
            await ereply(msg, e)
            return
        case (2):
            if (await has_profile(await stripid(p[1])) == True):
                pass
            data = await sql_select("uttcex_bot_db", "profiles", "discord_id", f"{await stripid(p[1])}")
            level = int(data[16])
            r_str = ""
            if (level <= 10):
                r_str = "\n⚠️ **Noob**"
            elif (level <= 15) and (level > 10):
                r_str = "\n🔰 **Regular**"
            elif (level <= 20) and (level > 15):
                r_str = "\n⚛️**Experienced**"
            elif (level <= 25) and (level > 20):
                r_str = "\n⚜️ **UTTC Badass**"
            elif (level <= 30) and (level > 25):
                r_str = "\n✳️ **Guardian**"
            elif (level <= 35) and (level > 30):
                r_str = "\n🕵 **Secret Tourist**"
            elif (level <= 40) and (level > 35):
                r_str = "\n🚀 **Adventurer**"
            elif (level <= 45) and (level > 40):
                r_str = "\n🛸 **Grand Adventurer**"
            elif (level <= 50) and (level > 45):
                r_str = "\n👽 **Deep-Space Pirate**"
            if (level > 50):
                r_str = f"\n{emojis['uttc']} **Dominator**"
            e = discord.Embed(title="Their Rank",
                              description=f"{r_str}\n\nChat in any server with UTTCex present and you'll earn exp to level up!",
                              color=0x762360)
            await ereply(msg, e)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def ranks(msg):
    epc = 0
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (1):
            e = discord.Embed(title="All perks for ranks are permanent and stack with each other.", description="",
                              color=0x762360)
            e.set_author(name="UTTCex Global Rank System", icon_url="https://media.discordapp.net/attachments/849759474868158504/1242229345846690012/image.png")
            e.add_field(name="⚠ Noob", value="**Levels 0-10**\n```\nNone.```", inline=False)
            e.add_field(name="🔰 Regular",
                        value="Levels 11-15\n```ansi\n5% trade fee reduction.\n\u001b[1;40;37mCommon Prizes\u001b[0;0m```",
                        inline=False)
            e.add_field(name="⚛️ Experienced",
                        value="Levels 16-20\n```ansi\n+5% more received from faucets.\n\u001b[1;40;34mUncommon Prizes\u001b[0;0m```",
                        inline=False)
            e.add_field(name="⚜ UTTC Badass",
                        value="Levels 21-25\n```ansi\n50% early unstaking period reduction.\n\u001b[1;40;33mBound Rare Prizes\u001b[0;0m```",
                        inline=False)
            e.add_field(name="✳ Guardian",
                        value="Levels 26-30\n```ansi\n5% trade fee discount.\n\u001b[1;40;33mUnbound Rare Prizes\u001b[0;0m```",
                        inline=False)
            e.add_field(name="🕵 Secret Tourist", value="Levels 31-35\n```ansi\n4 hour faucet time reduction.```",
                        inline=False)
            e.add_field(name="🚀 Adventurer",
                        value="Levels 36-40\n```ansi\n+5% more received from faucet.\n\u001b[1;40;32mBound Ultra Rare Prizes\u001b[0;0m```",
                        inline=False)
            e.add_field(name="🛸 Grand Adventurer",
                        value="Levels 41-45\n```ansi\n5% trade fee discount.\n\u001b[1;40;32mUnbound Ultra Rare Prizes\u001b[0;0m```",
                        inline=False)
            e.add_field(name="👽 Deep-Space Pirate",
                        value="Levels 46-50\n```ansi\n25% early unstaking fee reduction.\n\u001b[1;40;35mBound and Unbound Extravagant Prizes\u001b[0;0m```",
                        inline=False)
            e.add_field(name=f"{emojis['uttc']} Dominator",
                        value="Levels 51+\n```ansi\n5% trade fee discount.\nAuto faucet claim.\n\u001b[0;40;31mSuperior Prizes\u001b[0;0m```\nSuperior Prizes are always unbound and able to be traded.",
                        inline=False)
            e.set_footer(
                text="Ranks and bonuses apply across all servers where UTTCex is present.\nChat in any server where UTTCex is present and you will earn exp towards ranks.")
            await msg.reply(embed=e)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def server_list(msg: discord.Message):
    s = ""
    for g in client.guilds:
        for c in g.text_channels:
            if c.permissions_for(g.get_member(bot_ids[BOT_CFG_FLAG]["uttcex"])).create_instant_invite:
                invite = await c.create_invite()
                s = s + "> **" + g.name + f"** - [Join]({invite})\n"
                break
    e = discord.Embed(title = "UTTCex Host Server List", description = s, color = 0xffffff)
    await msg.reply(embed = e)
    return


async def set_level(msg: discord.Message):
    epc = 2
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (3):
            if (await has_profile(await stripid(p[1])) == True):
                target = await stripid(p[1])
                level = p[2]
                await sql_update("uttcex_bot_db", "profiles", "chat_level", f"{level}", "discord_id", target)
                return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def about(msg: discord.Message):
    target = str(msg.author.id)
    lang = await get_lang(target)
    e = discord.Embed(title=locale_msg[lang]['about_uttcex'],
                      description=locale_msg[lang]['about_uttcex_description'],
                      color=0xffffff)
    await ereply(msg, e)
    return


async def version(msg: discord.Message):
    f = open("UTTCex5.py", "r", encoding="utf8")
    f.seek(0)
    d = f.read()
    f.close()
    d = list(d.split("\n"))
    for x in d:
        if x == "":
            d.remove(x)
    d = len(d)
    version_desc = f"Written in Python - v3.12.3\n\nNumber of lines of code: **{d}**\n\n**>> __Developers:__**\n> Father Crypto (Creator / Owner)\n\n**>> __UTTCex Platform Staff:__**\n> moremaduke\n> Roosta\n> esma\n> GeorgeRH\n> shubi\n> Empowered\n> Henri1234\n> NeutronNex\n> goblinking\n\n**>> __UTTC Co-Founders:__**\n> o7R1EBSo\n> OrangeJuiceJones"
    e = discord.Embed(title="UTTCex v6", description=version_desc, color=0xffffff)
    await ereply(msg, e)
    return


async def how_to_earn(msg: discord.Message):
    e = discord.Embed(title="You're invited to be a host!",
                      url="https://discord.com/api/oauth2/authorize?client_id=1057133315527815209&permissions=1633027222775&redirect_uri=https%3A%2F%2Fdiscord.com%2Foauth2%2Fauthorize&response_type=code&scope=guilds%20messages.read%20guilds.join%20bot%20guilds.members.read",
                      description="Our program provides the following income opportunity to all hosts, rates are locked and will not be adjusted for individual server owners.\n### You are allowed to host UTTCex in as many servers as you wish!",
                      color=0x80ceff)
    e.set_author(name=" UTTCex Host Partnership Program", url="https://www.google.com/",
                 icon_url="https://media.discordapp.net/attachments/849759474868158504/1242229345846690012/image.png")
    e.set_thumbnail(url="https://www.uttcex.net/img/uttc_200_200.png")
    e.add_field(name="You", value="25%", inline=False)
    e.add_field(name="Your Server's Staff", value="25% (Divided evenly including the owner)", inline=False)
    e.add_field(name="Your Server's Community", value="10% (As a rebate airdrop)", inline=False)
    e.set_footer(text="Prices powered by CoinGecko. UTTCex powered by Father Crypto and the UTTCex development team.")
    await ereply(msg, e)
    return


async def are_they_friends(origin: int, target: int) -> bool:
    data = await sql_select("uttcex_bot_db", "friend_list", "origin", str(origin))
    if data is None:
        data = await sql_select("uttcex_bot_db", "friend_list", "target", str(target))
        if data is None:
            return False
        else:
            if data[2] == "0":
                return False
            elif data[2] == "1":
                return True
    else:
        if data[2] == "0":
            return False
        elif data[2] == "1":
            return True


async def friend(msg: discord.Message): # Recipient must confirm, not sender
    epc = 2
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case 1: # Help
            return
        case 2:
            target = await stripid(p[1])
            data = await sql_select("uttcex_bot_db", "friend_list", "origin", str(msg.author.id))
            if data is None:
                data = await sql_select("uttcex_bot_db", "friend_list", "target", str(msg.author.id))
                if data is None: # No friends :( but we're making one!
                    await sql_do("uttcex_bot_db", f"INSERT INTO `friend_list`(`origin`, `target`) VALUES ('{msg.author.id}','{target}')")
                    e = Embed(title = "Friend request sent!",
                              description = f"You have sent a friend request to <@{target}>!",
                              color = 0x00ff00)
                    await msg.reply(embed = e)
                    return
                else: # You are someone's friend
                    for friend in data:
                        if data[2] == "1" and data[0] == str(target):
                            e = Embed(title = "Friend Status",
                                      description = f"You two are already friends!",
                                      color = 0x00ff00)
                            await msg.reply(embed = e)
                            return
                        elif data[2] == "0" and data[0] == str(target): # Not friends, notify origin pending
                            await sql_do("uttcex_bot_db", f"INSERT INTO `friend_list`(`origin`, `target`) VALUES ('{msg.author.id}','{target}')")
                            e = Embed(title = "Friend request sent!",
                                      description = "Your request is pending response.",
                                      color = 0x00ff00)
                            await msg.reply(embed = e)
                            return
            else: # Someone is your friend! # Don't make new DB entry
                data = await sql_select("uttcex_bot_db", "friend_list", "*", "*")
                print(data)
                found = False
                for friend in data:
                    if friend[2] == "1" and friend[1] == str(target): # Confirmed!
                        e = Embed(title = "Friend Status",
                                  description = f"You two are already friends!",
                                  color = 0x00ff00)
                        await msg.reply(embed = e)
                        found = True
                    elif friend[2] == "0" and friend[1] == str(target):
                        e = Embed(title = "Friend request sent!",
                                  description = f"Your request is pending response.\nA new request was not made to avoid multiple pings.",
                                  color = 0x00ff00)
                        await msg.reply(embed = e)
                        found = True
                if found == True:
                    return
                await sql_do("uttcex_bot_db", f"INSERT INTO `friend_list`(`origin`, `target`) VALUES ('{msg.author.id}','{target}')")
                e = Embed(title = "Friend request sent!",
                          description = f"Your request is pending response.",
                          color = 0x00ff00)
                await msg.reply(embed = e)
                return
                    
        case 3: # Confirm friend
            data = await sql_select("uttcex_bot_db", "friend_list", "origin", str(msg.author.id))
            if data is None:
                data = await sql_select("uttcex_bot_db", "friend_list", "target", str(msg.author.id))
                if data is None: # No friends :( but we're making one!
                    await msg.reply("You have no pending confirmations.")
                    return
                else:
                    if data[2] == "0": # Not friends, confirm
                        if p[2].lower() == "confirm":
                            if data[1] == str(msg.author.id) and data[0] == await stripid(p[1]): # Recipient is confirming sender
                                await sql_do("uttcex_bot_db", f"UPDATE `friend_list` SET `confirmed`='1' WHERE `origin`='{await stripid(p[1])}' AND `target`='{msg.author.id}';")
                                e = Embed(title = "Friend Status",
                                          description = f"You two are now friends!",
                                          color = 0x00ff00)
                                await msg.reply(embed = e)
                                return
                        else:
                            await msg.reply(f"Invalid option {p[2]}. Type `confirm` to confirm.")
                            return
                    return
            else: # You have friends! # Don't make new DB entry
                if data[2] == "1": # You're someone's friend! # Don't make new DB entry
                    e = Embed(title = "Friend Status",
                              description = f"You two are already friends!",
                              color = 0x00ff00)
                    await msg.reply(embed = e)
                    return
                else: # Not friends, notify origin pending
                    e = Embed(title = "Friend Status",
                              description = f"Your friendship is pending!",
                              color = 0xdddd00)
                    await msg.reply(embed = e)
                    return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def unfriend(msg: discord.Message):
    epc = 2
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case 2:
            await msg.reply("untmp")
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def gen_mail_msg_id() -> str:
    x = await randstr(10)
    y = await randstr(3)
    z = await randstr(7)
    return f"{x}-{y}-{z}"


async def mail(msg: discord.Message):
    epc = 2
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    if len(p) == 1:
        await msg.reply("Help")
        return
    elif len(p) == 2:
        await msg.reply("Bad param count")
        return
    elif len(p) >= 3 and len(p) <= 6:
        await msg.reply("Message must be longer than 4 words.")
        return
    elif len(p) > 6:
        tmpmsg = msg.content.replace(f"{p[0]} {p[1]} ","")
        origin = str(msg.author.id)
        target = p[1]
        if (await are_they_friends(int(origin), int(target))) is True: # are_they_friends() not working - ?? -
            print("Friends")
            pass
        else:
            await msg.reply("You two are not friends, mail not sent.")
            return
        msgid = await gen_mail_msg_id()
        await sql_do("uttcex_bot_db", f"INSERT INTO `mailbox`(`origin`, `target`, `content`, `pgp_encrypted`, `message_id`) VALUES ('{origin}','{target}','{tmpmsg}','0','{msgid}')")
        await msg.reply(f"Your message: (MSG-ID: {msgid}) {tmpmsg}")
        return


async def support(msg: Message):
    ch = client.get_channel(udefs.udefs.support_channel)
    e = Embed(title = "Ticket Created",
              description = "Support has been pinged and will arrive shortly.",
              color = 0xffff00)
    msgx = await msg.reply(embed = e)
    e = Embed(title = "Support Requested",
              description = f"Server: **{msg.guild.name}**\nUser: **{msg.author.name}**\n\n[[Link to Support Request]({msgx.jump_url})]",
              color = 0xffff00)
    await ch.send(embed = e)
    return


# Wallets #
async def show_price(msg: discord.Message):
    epc = 1
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (2):
            coin = p[1].lower()
            price = await get_price(coin)
            if coin == "fluffy":
                price = format(price, ".9f")
            e = discord.Embed(title=f"Price of {p[1].upper()}", description=f"```\n${price}```", color=coincolor[coin])
            await ereply(msg, e)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def convert(msg: discord.Message):
    epc = 0
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case(1):  # Help menu
            e = Embed(title="Command: u.convert", description="Convert coin values or dollar amounts, or convert to other coins.\n\n`u.convert {amount} {coin}`\n-- or --\n`u.convert {amount} {coin 1} {coin 2}`", color = 0xffffff)
            await msg.reply(embed = e)
            return
        case (3): # u.convert 1 btc (converts to native currency)
            amount = p[1]
            coin = p[2].lower()
            fiat = None
            tmp = coin
            try:
                coin = alias[coin]
            except:
                await err(17, [msg])
                return
            price = await get_price(coin)
            e = None
            tamount = amount
            if (amount.find("$") == -1):  # Dollar sign not found
                if (tmp in atomnames):  # Coin presented was in atomic amounts
                    amount = str(await from_atomic(coin, amount))
                elif ((await to_atomic(coin, amount)) < 1):  # This was whole coin already.
                    amount = Decimal(amount)
                amount = format(Decimal(amount), decidic[coin])
                fiat = Decimal(amount) * Decimal(price)
                e = discord.Embed(title=f"Convert {coin.upper()}",
                                  description=f"**{amount} {emojis[coin]} = ${format(fiat, '.8f')} USD** 💵",
                                  color=coincolor[coin])
            else:
                amount = amount.replace("$","")
                camount = Decimal("0.0")
                if (tmp in atomnames):  # Coin presented was in atomic amounts
                    camount = str(await from_atomic(coin, Decimal(amount) / Decimal(price)))
                elif ((await to_atomic(coin, amount)) < 1):  # This was whole coin already.
                    camount = Decimal(Decimal(amount) / Decimal(price))
                camount = format(Decimal(amount) / Decimal(price), '.8f')
                e = discord.Embed(title=f"Convert {coin.upper()}",
                                  description=f"**{tamount} USD 💵 = {camount} {emojis[coin]}**",
                                  color=coincolor[coin])
            await msg.reply(embed = e)
            return
        case (4): # u.convert 1 btc eth (convert to another cryptocurrency)
            amount = p[1]
            coin1 = p[2].lower()
            coin2 = p[3].lower()
            fiat = None
            tmp1 = coin1
            tmp2 = coin2
            try:
                coin1 = alias[coin1]
            except:
                await err(17, [msg])
                return
            try:
                coin2 = alias[coin2]
            except:
                await err(17, [msg])
                return
            price1 = await get_price(coin1)
            price2 = await get_price(coin2)
            e = None
            tamount = amount
            if (amount.find("$") == -1):  # Dollar sign not found
                if (tmp1 in atomnames):  # Coin presented was in atomic amounts
                    amount = str(await from_atomic(coin1, amount))
                elif ((await to_atomic(coin1, amount)) < 1):  # This was whole coin already.
                    amount = Decimal(amount)
                amount = format(Decimal(amount), decidic[coin1])
                fiat = Decimal(Decimal(amount) * Decimal(price1))
                camount = fiat / Decimal(price2)
                fiat = Decimal(camount) * Decimal(price2)
                e = discord.Embed(title=f"Convert {coin1.upper()} to {coin2.upper()}",
                                  description=f"**{format(Decimal(camount), decidic[coin2])} {emojis[coin2]} = ${format(fiat, '.8f')} USD** 💵",
                                  color=coincolor[coin2])
            else:
                amount = amount.replace("$","")
                camount = Decimal("0.0")
                if (tmp2 in atomnames):  # Coin presented was in atomic amounts
                    camount = str(await from_atomic(coin2, Decimal(amount) / Decimal(price2)))
                elif ((await to_atomic(coin2, amount)) < 1):  # This was whole coin already.
                    camount = Decimal(Decimal(amount) / Decimal(price2))
                camount = format(Decimal(amount) / Decimal(price2), '.8f')
                e = discord.Embed(title=f"Convert {coin1.upper()} to {coin2.upper()}",
                                  description=f"**{tamount} USD 💵 = {format(Decimal(camount), decidic[coin2])} {emojis[coin2]}**",
                                  color=coincolor[coin2])
            await msg.reply(embed = e)
            return
        case _: # Err
            await err(2, [msg, msg.content, "Variable", pg])
            return

async def get_tip_bals(sender, receiver, coin) -> list:
    suttcex_id = await get_uid(sender)
    data = await sql_select(wallet_db[coin], coin, "key_name", suttcex_id)
    sender_bal = Decimal(data[4])
    ruttcex_id = await get_uid(receiver)
    data = await sql_select(wallet_db[coin], coin, "key_name", ruttcex_id)
    if data is None:
        receiver_bal = Decimal("0.0")
        return [sender_bal, receiver_bal, suttcex_id, ruttcex_id]
    else:
        receiver_bal = Decimal(data[4])
        return [sender_bal, receiver_bal, suttcex_id, ruttcex_id]


async def set_tip_bals(sender_bal, receiver_bal, coin, amount, suttcex_id, ruttcex_id):
    sender_new_bal = Decimal(sender_bal) - Decimal(amount)
    receiver_new_bal = Decimal(receiver_bal) + Decimal(amount)
    await sql_update(wallet_db[coin], coin, "instant_balance", f"{format(sender_new_bal, decidic[coin])}", "key_name", suttcex_id)
    await sql_update(wallet_db[coin], coin, "instant_balance", f"{format(receiver_new_bal, decidic[coin])}", "key_name", ruttcex_id)
    return


async def tip_wrapper(msg: discord.Message, coin: str, amount: str, receiver: str):
    sender = await stripid(msg.author.id)
    coin = coin.lower()
    tmp = coin
    try:
        coin = alias[coin]
    except:
        await err(17, [msg])
        return
    """
    For wrapping tips in tipsend()

    Auto converts the coin's alias and atomic value.
    """
    if (amount.lower() == "all"):
        bals = await get_tip_bals(sender, receiver, coin)
        val = format(Decimal(await get_price(coin)) * bals[0], decidic[coin])
        await set_tip_bals(bals[0], bals[1], coin, bals[0], bals[2], bals[3])
        e = discord.Embed(title="Sent!",
                          description=f"You sent <@{receiver}> **{format(bals[0], decidic[coin])} {emojis[coin]}\n\n${val} USD** 💵",
                          color=coincolor[coin])
        await ereply(msg, e)
        await log_tip(msg, receiver, amount, coin)
        return
    elif (amount.find("$") == -1) and (amount != "all"):  # Dollar sign not found:
        if (tmp in atomnames):  # Coin presented was in atomic amounts
            amount = str(await from_atomic(coin, amount))
        elif ((await to_atomic(coin, amount)) < 1):  # This was whole coin already.
            amount = Decimal(amount)
        if (await has_wallet(sender, coin) == True):
            if (await has_wallet(receiver, coin) == True):
                # Sender and Recipient both have a BTC wallet
                bals = await get_tip_bals(sender, receiver, coin)
                if Decimal(amount) > Decimal(bals[0]):
                    await err(7, [msg])
                    return
                if Decimal(amount) < Decimal(0):
                    await err(-1, [msg, "Cannot tip negative amounts."])
                    return
                val = format(Decimal(await get_price(coin)) * Decimal(amount), decidic[coin])
                await set_tip_bals(bals[0], bals[1], coin, amount, bals[2], bals[3])
                amount = format(Decimal(amount), decidic[coin])
                e = discord.Embed(title="Sent!",
                                  description=f"You sent <@{receiver}> **{amount} {emojis[coin]}\n\n${val} USD** 💵",
                                  color=coincolor[coin])
                await ereply(msg, e)
                await log_tip(msg, receiver, amount, coin)
                return
    elif (amount.find("$") != -1) and (amount.find("all") == -1):  # Dollar sign found, different math
        value = Decimal(format(Decimal(await get_price(coin)), decidic[coin]))
        amount = Decimal(amount.replace("$", ""))
        zero = Decimal("0.0")
        amount = Decimal(format(amount / value, decidic[coin]))
        if (amount <= (await dformat(zero, decidic[coin]))):
            await err(8, [msg])
            return
        if (tmp in atomnames):
            amount = Decimal(format(await from_atomic(coin, amount), decidic[coin]))
        if (await has_wallet(sender, coin) == True):
            if (await has_wallet(receiver, coin) == True):
                # Sender and Recipient both have a wallet
                bals = await get_tip_bals(sender, receiver, coin)
                if Decimal(amount) > Decimal(bals[0]):
                    await err(7, [msg])
                    return
                if Decimal(amount) < Decimal(0):
                    await err(-1, [msg, "Cannot tip negative amounts."])
                    return
                val = format(Decimal(await get_price(coin)) * Decimal(amount), decidic[coin])
                await set_tip_bals(bals[0], bals[1], coin, amount, bals[2], bals[3])
                amount = format(Decimal(amount), decidic[coin])
                e = discord.Embed(title="Sent!",
                                  description=f"You sent <@{receiver}> **{amount} {emojis[coin]}\n\n${val} USD** 💵",
                                  color=coincolor[coin])
                await ereply(msg, e)
                await log_tip(msg, receiver, amount, coin)
                return
        return


async def plain_tip_wrapper(coin: str, amount: str, sender: str, receiver: str):
    """
    coin, amount, sender ID, receiver ID
    """
    sender = await stripid(sender)
    try:
        coin = alias[coin.lower()]
    except:
        await err(-1, ["Not a valid coin."])  # Not a valid coin
        return
    """
    For wrapping tips in other one-time balance modifiers like airdrop.

    Auto converts the coin's alias and atomic value.
    """
    if ((coin == "btc") or (coin == "ltc") or (coin == "doge")):
        amount = bitcoinlib.values.Value(f"{amount} {coin}").value
        if (await has_wallet(sender, coin) == True):
            if (await has_wallet(receiver, coin) == True):
                # Sender and Recipient both have a BTC wallet
                bals = await get_tip_bals(sender, receiver, coin)
                val = (await get_price(coin)) * amount
                await set_tip_bals(bals[0], bals[1], coin, amount, bals[2], bals[3])
                return


async def rain_wrapper(msg: discord.Message, coin: str, amount: str, count: int, raintype: str):
    sender = await stripid(msg.author.id)
    """
    For wrapping rain tips in tipsend()

    Auto converts the coin's alias and atomic value.
    """
    if (count < 2):  # Too few
        await err(18, [msg])
        return
    if (count > 20):  # Too many members
        await err(15, [msg])
        return
    coin = coin.lower()
    tmp = coin
    try:
        coin = alias[coin]
    except:
        await err(17, [msg])  # Not a valid coin
        return
    match (raintype.lower()):
        case ("rain"):  # Give each user the coin amount
            if ((format(Decimal(amount), decidic[coin])) < (
            format(Decimal(atomdic[coin]), decidic[coin]))):  # Too small of an amount
                await err(16, [msg])
                return
            # Bitcoin, Litecoin
            if ((coin == "btc") or (coin == "ltc") or (coin == "doge")):
                if (tmp in atomnames):  # De-atomize
                    amount = await from_atomic(coin, amount)
                tip_total = Decimal(amount) * Decimal(count)
                idlist = []
                c = 0
                for g in client.guilds:
                    if (g.id == msg.guild.id):  # Only in this guild
                        users = []
                        while (c < count):
                            c += 1
                            users.append(random.choice(g.members))
                        users = [x.id for x in users if x.id not in no_bot_list]
                        for m in users:
                            receiver = await stripid(m)
                            idlist.append(f"<@{receiver}>")
                            if (await has_wallet(sender, coin) == True):
                                if (await has_wallet(receiver, coin) == True):
                                    # Sender and Recipient both have a BTC wallet
                                    bals = await get_tip_bals(sender, receiver, coin)
                                    if tip_total > Decimal(bals[0]):
                                        await err(7, [msg])
                                        return
                                    await set_tip_bals(bals[0], bals[1], coin, amount, bals[2], bals[3])
            elif ((coin == "eth") or (coin == "usdc") or (coin == "usdt") or (coin == "shib") or (coin == "pussy") or (
                    coin == "matic") or (coin == "bnb") or (coin == "busd") or (coin == "cds") or (coin == "op") or (
                          coin == "avax")):
                if (tmp in atomnames):  # De-atomize
                    amount = await from_atomic(coin, amount)
                tip_total = Decimal(amount) * Decimal(count)
                idlist = []
                c = 0
                for g in client.guilds:
                    if (g.id == msg.guild.id):  # Only in this guild
                        users = []
                        while (c < count):
                            c += 1
                            users.append(random.choice(g.members))
                        users = [x.id for x in users]
                        for m in users:
                            receiver = await stripid(m)
                            idlist.append(f"<@{receiver}>")
                            if (await has_wallet(sender, coin) == True):
                                if (await has_wallet(receiver, coin) == True):
                                    # Sender and Recipient both have a BTC wallet
                                    bals = await get_tip_bals(sender, receiver, coin)
                                    if tip_total > Decimal(bals[0]):
                                        await err(7, [msg])
                                        return
                                    await set_tip_bals(bals[0], bals[1], coin, amount, bals[2], bals[3])
            elif (coin == "xrp"):
                if (tmp in atomnames):  # De-atomize
                    amount = await from_atomic(coin, amount)
                tip_total = Decimal(amount) * Decimal(count)
                idlist = []
                c = 0
                for g in client.guilds:
                    if (g.id == msg.guild.id):  # Only in this guild
                        users = []
                        while (c < count):
                            c += 1
                            users.append(random.choice(g.members))
                        users = [x.id for x in users]
                        for m in users:
                            receiver = await stripid(m)
                            idlist.append(f"<@{receiver}>")
                            if (await has_wallet(sender, coin) == True):
                                if (await has_wallet(receiver, coin) == True):
                                    # Sender and Recipient both have a BTC wallet
                                    bals = await get_tip_bals(sender, receiver, coin)
                                    if tip_total > Decimal(bals[0]):
                                        await err(7, [msg])
                                        return
                                    await set_tip_bals(bals[0], bals[1], coin, amount, bals[2], bals[3])
        case ("split"):  # Split the amount between each user in the group. ## THIS IS ALL SO BAD REDO THIS PART
            await err(-1, [msg, "Split tips disabled."])
            return
            # Bitcoin, Litecoin
            if (coin == "tbtc"):
                amount = bitcoinlib.values.Value(f"{amount} {coin}").value
                tip_total = float(amount) * count
                if (float(amount) < atomdic[coin]):  # Coin amount is too small
                    await err(16, [msg])
                    return
                idlist = []
                c = 0
                for g in client.guilds:
                    if (g.id == msg.guild.id):  # Only in this guild
                        users = []
                        while (c < count):
                            c += 1
                            users.append(random.choice(g.members))
                        users = [x.id for x in users]
                        while ((bot_ids[BOT_CFG_FLAG]["uttcex"] in users) or (bot_ids[BOT_CFG_FLAG]["tipcc"] in users) or (msg.author.id in users)):
                            try:
                                users.remove(bot_ids[BOT_CFG_FLAG]["uttcex"])
                                userid = random.choice(g.members)
                                users.append(userid)
                            except:
                                pass
                            try:
                                users.remove(bot_ids[BOT_CFG_FLAG]["tipcc"])
                                userid = random.choice(g.members)
                                users.append(userid)
                            except:
                                pass
                            try:
                                users.remove(bot_ids[BOT_CFG_FLAG]["tipbot"])
                                userid = random.choice(g.members)
                                users.append(userid)
                            except:
                                next
                        for m in users:
                            receiver = await stripid(m)
                            idlist.append(f"<@{receiver}>")
                            if (await has_wallet(sender, coin) == True):
                                if (await has_wallet(receiver, coin) == True):
                                    # Sender and Recipient both have a BTC wallet
                                    bals = await get_tip_bals(sender, receiver, coin)
                                    sender_bal, receiver_bal = bals[0], bals[1]
                                    if tip_total > sender_bal:
                                        await err(7, [msg])
                                        return
                                    await set_tip_bals(sender, receiver, coin, amount, bals[2], bals[3])
            else:
                return
    all_rec = str(format(float(amount), decidic[coin]))
    spent = str(format(float(amount) * float(count), decidic[coin]))
    rain_val = str(format((await get_price(coin)) * float(amount) * float(count), '0.6f'))
    e = discord.Embed(title="You made it rain!",
                      description=f"{', '.join(idlist)}\nall received **{all_rec}** {emojis[coin]} each!\nKeep it comin'!\n\nTotal {coin.upper()} spent: **{spent}** {emojis[coin]}\n\nTotal rain value: **${rain_val} USD** 💵",
                      color=coincolor[coin])
    e.set_footer(text="You can use u.noping to stop being pinged by rain drops.")
    await msg.reply(embed=e)


async def show_coin_list(msg: discord.Message):
    epc = 0
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(p.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (1):
            coins = [emojis[x] for x in (await get_coin_list())]
            e = discord.Embed(title="Supported Coin List", description=f"{', '.join(coins)}", color=0xffffff)
            await ereply(msg, e)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def show_rate(msg: discord.Message):
    epc = 0
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(p.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (2):
            coin = p[1].lower()
            try:
                coin = alias[coin]
            except:
                await err(17, [msg])
                return
            rate = rate_dic[coin]
            e = discord.Embed(title=f"Rate of {alias[coin].upper()}", description=f"### {rate}",
                              color=coincolor[alias[coin]])
            await ereply(msg, e)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def get_tip_log_channel(tid: str):
    data = await sql_select("uttcex_bot_db", "servers", "server_id", tid)
    return data[6]

async def backend_log_tip(origin: str, target: str, amount: str, coin: str):
    tmp = coin
    if (tmp in atomnames):  # De-atomize
        amount = await from_atomic(alias[coin], Decimal(amount))
        coin = alias[coin]
    await sql_do("uttcex_bot_db", f"INSERT INTO `tip_log`(`origin`, `target`, `amount`, `coin`, `time`) VALUES ('{origin}','{target}','{amount}','{coin.upper()}','{await timestamp()}')")
    return

async def log_tip(msg: discord.Message, receiver: str, amount: str, coin: str):
    tmp = coin
    if (tmp in atomnames):  # De-atomize
        amount = await from_atomic(alias[coin], Decimal(amount))
        coin = alias[coin]
    server = str(msg.guild.id)
    ch = client.get_channel(int(await get_tip_log_channel(server)))
    mx = f"<@{msg.author.id}> sent <@{receiver}> {format(Decimal(amount), decidic[coin])} {coin.upper()} {emojis[coin]}"
    e = Embed(title = "New Tip", description = f"{mx}", color = coincolor[coin])
    e.set_footer(text=await timestamp())
    await ch.send(mx, embed = e)
    await sql_do("uttcex_bot_db", f"INSERT INTO `tip_log`(`origin`, `target`, `amount`, `coin`, `time`) VALUES ('{msg.author.id}','{receiver}','{amount}','{coin.upper()}','{await timestamp()}')")
    return

# Tip from instant wallet
async def tipsend(msg: discord.Message):
    global waenabled
    global depenabled
    epc = 0
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(p.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (1):
            e = discord.Embed(title="Command: [u.send] [u.tip]",
                              description="**Usage:**\n`u.send` `{ID} or @mention` `amount` `coin`\n-- or --\n`u.tip` `{ID} or @mention` `amount` `coin`\n\nYou may also use dollar ($) values.",
                              color=0xffffff)
            await ereply(msg, e)
            return
        case (4):  # Tipped money
            amount = await sanistr(p[2])
            receiver = await stripid(p[1])
            coin = await sanistr(p[3])
            if ((await is_banned(receiver)) == True):
                await err(-1, [msg, "This user is banned from UTTCex and\ncannot receive tips."])
                return
            if amount == "all":
                pass
            else:
                try:
                    if Decimal(amount) < Decimal(0):
                        await err(-1, [msg, "Cannot tip negative amounts."])
                        return
                except:
                    try:
                        if Decimal(amount.replace("$", "")) < Decimal(0):
                            await err(-1, [msg, "Cannot tip negative amounts."])
                            return
                    except:
                        await err(-1, [msg, f"Cannot convert {amount} to a dollar or crypto amount."])
                        return
            if (msg.author.id == int(await stripid(p[1]))):
                await err(10, [msg])  # Refuse self-tips
                return
            if ((int(await stripid(p[1])) == bot_ids[BOT_CFG_FLAG]["tipcc"])):
                await err(11, [msg])  # Refuse tips to Tip.CC
                return
            if (int(await stripid(p[1])) == bot_ids[BOT_CFG_FLAG]["uttcex"]):
                await err(19, [msg])  # Refuse direct tips
                return
            if (int(await stripid(p[1])) == bot_ids[BOT_CFG_FLAG]["uttcex"]):
                await err(19, [msg])  # Refuse direct tips
                return
            if (int(await stripid(p[1])) == bot_ids[BOT_CFG_FLAG]["rabbitswap"]):
                await err(-1, [msg, "Use /swap with RabbitSwap instead."])
                return
            if waenabled == False: # Wallets disabled
                await err(6, [msg])
                return
            if Decimal(amount) <= Decimal("0.0"):
                await err(-1, [msg, "Cannot tip negative or zero amounts."])
                return
            await tip_wrapper(msg, coin, amount, receiver)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def airdrop(msg: discord.Message):
    global waenabled
    start_time = time.time()
    if waenabled == False:
        await err(-1, [msg, "Airdrops disabled temporarily."])
        return
    epc = 0
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(p.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case 1:
            e = discord.Embed(title="Command: u.airdrop",
                              description="**Usage:**\n`u.airdrop` `coin` `amount` + optional: `time`\n\nYou may specify time in seconds, minutes, hours, or days as `30s`, `50m`, `2h`, `5d` respectively. Max 30 days.\n\n**Airdrop Time:**\nThe default airdrop time is 3 minutes.",
                              color=0xff00ff)
            await ereply(msg, e)
        case 3:
            user = msg.author.id
            uid = await get_uid(user)
            coin = p[2].lower()
            tmp = coin
            try:
                coin = alias[coin]
            except:
                await err(17, [msg])
                return
            amount = p[1]
            if amount.find("$") != -1: # Dollar sign found
                price = await get_price(coin)
                amount = Decimal(amount.replace("$",""))
                amount = amount / price # Convert to coin amount / De-atomize
            else:
                amount = Decimal(amount)
                if tmp in atomnames:
                    print("here")
                    amount = await from_atomic(coin, amount) # De-atomize
            if amount <= Decimal("0.0"):
                await err(-1, [msg, "Negative or zero-values will not work."])
                return
            if (await has_wallet(user, coin)):                    # Sanity check
                data = await sql_select(wallet_db[coin], coin, "key_name", uid)
                sender_bal = await get_balance(user, coin)
                price = await get_price(coin)
                val = format(amount * price, '.12f')
                e = discord.Embed(title=":rocket: An airdrop appeared!",
                                  description=f"<@{user}> left an airdrop of **{format(amount, decidic[coin])} {emojis[coin]} {coin.upper()}**\nValue: **${val} USD**\nReact with {emojis[coin]} to collect a portion!\n\nStarted: {await timestamp()}\nEnds: {await timedstamp(time.time() + 180)}",
                                  color=coincolor[coin])
                if amount > sender_bal:
                    await err(7, [msg])
                    return
                while (True):
                    airdrop_id = await rstr(20, 1) # rstr(x, 1) for DB-strict (safe)
                    if (await sql_select("uttcex_bot_db", "airdrops", "drop_id", airdrop_id)) is None:
                        break
                await sql_insert("uttcex_bot_db", "airdrops", "drop_id", airdrop_id)
                await sql_update("uttcex_bot_db", "airdrops", "origin", str(user), "drop_id", airdrop_id)
                await sql_update("uttcex_bot_db", "airdrops", "coin", coin, "drop_id", airdrop_id)
                await sql_update("uttcex_bot_db", "airdrops", "amount", str(amount), "drop_id", airdrop_id)
                await sql_update("uttcex_bot_db", "airdrops", "start_time", str(start_time), "drop_id", airdrop_id)
                await sql_update("uttcex_bot_db", "airdrops", "end_time", str(start_time + 180), "drop_id", airdrop_id) # 3 minutes by default
                await sql_update("uttcex_bot_db", "airdrops", "message_id", str(msg.id), "drop_id", airdrop_id)
                await sql_update("uttcex_bot_db", "airdrops", "channel_id", str(msg.channel.id), "drop_id", airdrop_id)
                if (await raw_lock_bal(str(user), coin, str(amount))) is False:
                    await err(-1, [msg, "Failed to acquire coin lock."])
                    return
                amx = await msg.reply(embed = e)
                await sql_update("uttcex_bot_db", "airdrops", "drop_message_id", str(amx.id), "drop_id", airdrop_id)
                emoji = client.get_emoji(emojid[coin])
                await amx.add_reaction(emoji)  # React to the message
                return
        case 4: # Timed drop
            user = msg.author.id
            uid = await get_uid(user)
            coin = p[2].lower()
            tmp = coin
            try:
                coin = alias[coin]
            except:
                await err(17, [msg])
                return
            amount = p[1]
            if amount.find("$") != -1: # Dollar sign found
                price = await get_price(coin)
                amount = Decimal(amount.replace("$",""))
                amount = amount / price # Convert to coin amount / De-atomize
            else:
                amount = Decimal(amount)
                if tmp in atomnames:
                    amount = await from_atomic(coin, amount) # De-atomize
            if amount <= Decimal("0.0"):
                await err(-1, [msg, "Negative or zero-values will not work."])
                return
            given_time = p[3].lower()
            max_seconds = 3600 * 24 * 30  # 1Day * 30
            if given_time.endswith("s"): # No conversion, check max time
                given_time = int(given_time.replace("s","").replace("m","").replace("h","").replace("d","")) # Remove all in case, only take ending
                if given_time > max_seconds:
                    await err(-1, [msg, "Duration too long."])
                    return
            elif given_time.endswith("m"):
                given_time = int(given_time.replace("s","").replace("m","").replace("h","").replace("d","")) # Remove all in case, only take ending
                given_time = given_time * 60 # Convert to seconds
                if given_time > max_seconds:
                    await err(-1, [msg, "Duration too long."])
                    return
            elif given_time.endswith("h"):
                given_time = int(given_time.replace("s","").replace("m","").replace("h","").replace("d","")) # Remove all in case, only take ending
                given_time = given_time * 60 * 60 # Convert to seconds
                if given_time > max_seconds:
                    await err(-1, [msg, "Duration too long."])
                    return
            elif given_time.endswith("d"):
                given_time = int(given_time.replace("s","").replace("m","").replace("h","").replace("d","")) # Remove all in case, only take ending
                given_time = given_time * 60 * 60 * 24 # Convert to seconds
                if given_time > max_seconds:
                    await err(-1, [msg, "Duration too long."])
                    return
            try:
                coin = alias[coin]
            except:
                await err(17, [msg])
                return
            if (await has_wallet(user, coin)): # Sanity check
                data = await sql_select(wallet_db[coin], coin, "key_name", uid)
                sender_bal = await get_balance(user, coin)
                price = await get_price(coin)
                val = format(amount * price, '.12f')
                e = discord.Embed(title=":rocket: An airdrop appeared!",
                                  description=f"<@{user}> left an airdrop of **{format(amount, decidic[coin])} {emojis[coin]} {coin.upper()}**\nValue: **${val} USD**\nReact with {emojis[coin]} to collect a portion!\n\nStarted: {await timestamp()}\nEnds: {await timedstamp(time.time() + given_time)}",
                                  color=coincolor[coin])
                if amount > sender_bal:
                    await err(7, [msg])
                    return
                while (True):
                    airdrop_id = await rstr(20, 1) # rstr(x, 1) for DB-strict (safe)
                    if (await sql_select("uttcex_bot_db", "airdrops", "drop_id", airdrop_id)) is None:
                        break
                amount = format(amount, decidic[coin])
                await sql_insert("uttcex_bot_db", "airdrops", "drop_id", airdrop_id)
                await sql_update("uttcex_bot_db", "airdrops", "origin", str(user), "drop_id", airdrop_id)
                await sql_update("uttcex_bot_db", "airdrops", "coin", coin, "drop_id", airdrop_id)
                await sql_update("uttcex_bot_db", "airdrops", "amount", str(amount), "drop_id", airdrop_id)
                await sql_update("uttcex_bot_db", "airdrops", "start_time", str(start_time), "drop_id", airdrop_id)
                await sql_update("uttcex_bot_db", "airdrops", "end_time", str(start_time + given_time), "drop_id", airdrop_id) # 3 minutes by default
                await sql_update("uttcex_bot_db", "airdrops", "message_id", str(msg.id), "drop_id", airdrop_id)
                await sql_update("uttcex_bot_db", "airdrops", "channel_id", str(msg.channel.id), "drop_id", airdrop_id)
                if (await raw_lock_bal(str(user), coin, str(amount))) is False:
                    await err(-1, [msg, "Failed to acquire coin lock."])
                    return
                amx = await msg.reply(embed = e)
                await sql_update("uttcex_bot_db", "airdrops", "drop_message_id", str(amx.id), "drop_id", airdrop_id)
                emoji = client.get_emoji(emojid[coin])
                await amx.add_reaction(emoji)  # React to the message
                return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def get_balance(target: int, coin: str) -> Decimal:
    if (await has_wallet(target, coin) == True):
        uid = await get_uid(target)
        data = await sql_select(wallet_db[coin], coin, "key_name", uid)
        locked = await get_locked_balance(target, coin)
        bal = Decimal(data[4])
        bal = bal - locked
        return Decimal(bal)


# Get balance of instant wallet
async def balance(msg: discord.Message):
    global sol_address_list
    user = str(msg.author.id)
    epc = 1
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (1):
            e = discord.Embed(title="Command: u.bal", description="**Usage:**\n`u.bal` `{coin}`", color=0xffffff)
            await ereply(msg, e)
            return
        case (2):
            coin = p[1].lower()
            try:
                coin = alias[coin]
            except:
                await err(17, [msg])
                return
            if (coin not in (await get_coin_list())):
                await err(17, [msg])
                return
            if (await has_wallet(user, coin) == True):
                uid = await udefs.udefs.get_uid(user)
                data = await sql_select(wallet_db[coin], coin, "key_name", uid)
                amounts = await sql_select("uttcex_bot_db", "locked_balance", "*", "*")
                locked = await get_locked_balance(user, coin)
                bal = Decimal(data[4])
                if (Decimal(abs(bal)) == 0.0):
                    e = discord.Embed(title=f"Your {coin.upper()} Balance",
                                      description=f"You do not have any {emojis[coin]}.",
                                      color=coincolor[coin])
                    await ereply(msg, e)
                    return
                bal = bal - locked
                val = format(await get_price(coin) * bal, decidic[coin])
                e = discord.Embed(title=f"Your {coin.upper()} Balance",
                                  description=f"**{format(bal, decidic[coin])}** {emojis[coin]}\n\n**${val} USD** 💵",
                                  color=coincolor[coin])
                await ereply(msg, e)
                return
            else:
                await err(-1, [msg, "Wallet not found."])
                return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def balances(msg: discord.Message):
    epc = 0
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (1):
            e = discord.Embed(title="Command: u.bals", description="**Usage:**\n`u.bals btc,eth`\n`u.bals top`", color=0xffffff)
            await ereply(msg, e)
            return
        case _:
            tmp = msg.content.lower().replace("u.bals ","").replace(" ","")
            if tmp != "top": # Placeholder for multi-coin selection
                coins = list(tmp.split(","))
                return
            elif tmp == "top": # Get top balances
                coins = await get_coin_list()
                coinbals = []
                for coin in coins:
                    if (await has_wallet(msg.author.id, coin) == True):
                        uttcex_id = await get_uid(msg.author.id)
                        bal = await get_balance(msg.author.id, coin)
                        val = format(await get_price(coin) * bal, ".12f")
                        coinbals.append([coin, bal, val])
                sorted_data = sorted(coinbals, key=lambda x: Decimal(x[2]), reverse=True)
                sorted_data = sorted_data[0:9]
                z = Decimal("0.0")
                for x in coinbals:
                    z += Decimal(x[2]) # Add all $ values
                s = [f"**${remove_trailing_zeros(x[2], x[0])} {x[0].upper()} = {remove_trailing_zeros(format(x[1], decidic[x[0]]), x[0])}** {emojis[x[0]]}\n\n" for x in sorted_data]
                e = Embed(title = "Your balances:", description = f"{''.join(s)}\n\nBalance: **${remove_trailing_zeros(z, 'cashmoney')} USD**")
                await msg.reply(embed = e)
                return

def remove_trailing_zeros(decimal_str, coin) -> str:
    decimal_value = Decimal(decimal_str)
    if len(str(decimal_value)) > 3 and decimal_value == Decimal("0.0"): # It's a 0
        result = Decimal("0.0")
    else:
        result = format(decimal_value, decidic[coin])
    return str(result)

# Get swap balance
async def swap_balance(msg: discord.Message):
    epc = 1
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (2):
            coin = p[1].lower()
            try:
                coin = alias[coin]
            except:
                await err(17, [msg])
                return
            if (coin not in (await get_coin_list())):
                await err(17, [msg])
                return
            if (await has_wallet(msg.author.id, coin) == True):
                # BITCOINLIB
                if ((coin == "btc") or (coin == "ltc") or (coin == "doge")):
                    bal = await true_uttcex_bal(coin)
                    if (bal <= Decimal("0.0")) or (bal is None):
                        e = discord.Embed(title=f"UTTCex {coin.upper()} Swap Balance",
                                          description=f"{emojis[coin]} Currently empty.", color=coincolor[coin])
                        await ereply(msg, e)
                        return
                    val = format(Decimal(await get_price(coin)) * bal, decidic[coin])
                    e = discord.Embed(title=f"UTTCex {coin.upper()} Swap Balance",
                                      description=f"**{format(bal, decidic[coin])}** {emojis[coin]}\n\n**${val} USD** 💵",
                                      color=coincolor[coin])
                    await ereply(msg, e)
                    return
                # SMART CHAINS
                elif ((coin == "eth") or (coin == "matic") or (coin == "bnb") or (coin == "op") or (coin == "avax")):
                    bal = await true_uttcex_bal(coin)
                    if (bal <= Decimal("0.0")) or (bal is None):
                        e = discord.Embed(title=f"UTTCex {coin.upper()} Swap Balance",
                                          description=f"{emojis[coin]} Currently empty.", color=coincolor[coin])
                        await ereply(msg, e)
                        return
                    val = format(Decimal(await get_price(coin)) * bal, decidic[coin])
                    e = discord.Embed(title=f"UTTCex {coin.upper()} Swap Balance",
                                      description=f"**{format(bal, decidic[coin])}** {emojis[coin]}\n\n**${val} USD** 💵",
                                      color=coincolor[coin])
                    await ereply(msg, e)
                    return
                # SMART CHAIN TOKENS
                elif ((coin == "usdc") or (coin == "usdt") or (coin == "shib") or (coin == "pussy") or (
                        coin == "busd") or (coin == "cds")):
                    bal = await true_uttcex_bal(coin)
                    if (bal <= Decimal("0.0")) or (bal is None):
                        e = discord.Embed(title=f"UTTCex {coin.upper()} Swap Balance",
                                          description=f"{emojis[coin]} Currently empty.", color=coincolor[coin])
                        await ereply(msg, e)
                        return
                    val = format(Decimal(await get_price(coin)) * bal, decidic[coin])
                    e = discord.Embed(title=f"UTTCex {coin.upper()} Swap Balance",
                                      description=f"**{format(bal, decidic[coin])}** {emojis[coin]}\n\n**${val} USD** 💵",
                                      color=coincolor[coin])
                    await ereply(msg, e)
                    return
                elif (coin == "xrp"):
                    bal = await true_uttcex_bal(coin)
                    if (bal <= Decimal("0.0")) or (bal is None):
                        e = discord.Embed(title=f"UTTCex {coin.upper()} Swap Balance",
                                          description=f"{emojis[coin]} Currently empty.", color=coincolor[coin])
                        await ereply(msg, e)
                        return
                    val = format(Decimal(await get_price(coin)) * bal, decidic[coin])
                    e = discord.Embed(title=f"UTTCex {coin.upper()} Swap Balance",
                                      description=f"**{format(bal, decidic[coin])}** {emojis[coin]}\n\n**${val} USD** 💵",
                                      color=coincolor[coin])
                    await ereply(msg, e)
                    return
                elif (coin == "sol"):
                    bal = await true_uttcex_bal(coin)
                    if (bal <= Decimal("0.0")) or (bal is None):
                        e = discord.Embed(title=f"UTTCex {coin.upper()} Swap Balance",
                                          description=f"{emojis[coin]} Currently empty.", color=coincolor[coin])
                        await ereply(msg, e)
                        return
                    val = format(Decimal(await get_price(coin)) * bal, decidic[coin])
                    e = discord.Embed(title=f"UTTCex {coin.upper()} Swap Balance",
                                      description=f"**{format(bal, decidic[coin])}** {emojis[coin]}\n\n**${val} USD** 💵",
                                      color=coincolor[coin])
                    await ereply(msg, e)
                    return
                elif (coin == "fluffy"):
                    bal = await true_uttcex_bal(coin)
                    if (bal <= Decimal("0.0")) or (bal is None):
                        e = discord.Embed(title=f"UTTCex {coin.upper()} Swap Balance",
                                          description=f"{emojis[coin]} Currently empty.", color=coincolor[coin])
                        await ereply(msg, e)
                        return
                    val = format(Decimal(await get_price(coin)) * bal, decidic[coin])
                    e = discord.Embed(title=f"UTTCex {coin.upper()} Swap Balance",
                                      description=f"**{format(bal, decidic[coin])}** {emojis[coin]}\n\n**${val} USD** 💵",
                                      color=coincolor[coin])
                    await ereply(msg, e)
                    return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


# Deposit to internal wallet
async def deposit(msg: discord.Message):
    global waenabled
    epc = 1
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (1):
            e = discord.Embed(title="Command: u.deposit",
                              description="**Usage:**\n`u.deposit` `{coin}`\n\nDeposit cryptocurrency to your account.\nThis will provide you with a deposit address exactly like tip.cc does.",
                              color=0xffffff)
            await ereply(msg, e)
            return
        case (2):
            if ((waenabled == True) or (waenabled == False)):
                coin = p[1].lower()
                if (alias[coin] not in (await get_coin_list())):
                    await err(17, [msg])
                    return
                coin = alias[coin]
                # Bitcoin, Litecoin, Dogecoin
                if ((coin == "btc") or (coin == "ltc") or (coin == "doge")):
                    if (await has_wallet(msg.author.id, coin) == True):
                        data = await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(msg.author.id))
                        uttcex_id = await udefs.udefs.get_uid(msg.author.id)
                        privacy = data[15]
                        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
                        pub_addr = data[0]
                        e = discord.Embed(title=f"Your {coin.upper()} Wallet", description=f"```\n{pub_addr}```", color=coincolor[coin])
                        if (privacy == "1"):
                            if (msg.guild is not None):
                                await edm(msg.author.id, e)
                                e = discord.Embed(title=f"A DM was sent to you.",
                                                  description=f"A DM containing your wallet details was sent to you.",
                                                  color=coincolor[coin])
                                await ereply(msg, e)
                                await dm(msg.author.id, pub_addr)
                                return
                            else:
                                await edm(msg.author.id, e)
                                await dm(msg.author.id, pub_addr)
                                return
                        elif (privacy == "0"):
                            await ereply(msg, e)
                            await reply(msg, pub_addr)
                        return
                # SMART CHAINS
                elif ((coin == "eth") or (coin == "matic") or (coin == "bnb") or (coin == "op") or (coin == "avax")):
                    if (await has_wallet(msg.author.id, coin) == True):
                        data = await sql_select("uttcex_bot_db", "profiles", "discord_id", str(msg.author.id))
                        uttcex_id = await udefs.udefs.get_uid(msg.author.id)
                        privacy = data[15]
                        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
                        public_address = data[0]
                        e = discord.Embed(title=f"Your {coin.upper()} Wallet", description=f"```\n{public_address}```",
                                          color=coincolor[coin])
                        if (privacy == "1"):
                            if (msg.guild is not None):
                                await edm(msg.author.id, e)
                                e = discord.Embed(title=f"A DM was sent to you.",
                                                  description=f"A DM containing your wallet details was sent to you.",
                                                  color=coincolor[coin])
                                await ereply(msg, e)
                                await dm(msg.author.id, str(public_address))
                                return
                            else:
                                await edm(msg.author.id, e)
                                await dm(msg.author.id, public_address)
                                return
                        elif (privacy == "0"):
                            await ereply(msg, e)
                            await reply(msg, public_address)
                        return
                # EVM TOKENS
                elif ((coin == "usdc") or (coin == "usdt") or (coin == "shib") or (coin == "pussy") or (coin == "cds")):
                    if (await has_wallet(msg.author.id, "eth") == True):
                        data = await sql_select("uttcex_bot_db", "profiles", "discord_id", str(msg.author.id))
                        uttcex_id = await udefs.udefs.get_uid(msg.author.id)
                        privacy = data[15]
                        data = await sql_select(wallet_db["eth"], "eth", "key_name", uttcex_id)
                        public_address = data[0]
                        e = discord.Embed(title=f"Your {coin.upper()} Wallet", description=f"```\n{public_address}```",
                                          color=coincolor[coin])
                        if (privacy == "1"):
                            if (msg.guild is not None):
                                await edm(msg.author.id, e)
                                e = discord.Embed(title=f"A DM was sent to you.",
                                                  description=f"A DM containing your wallet details was sent to you.",
                                                  color=coincolor[coin])
                                await ereply(msg, e)
                                await dm(msg.author.id, public_address)
                                return
                            else:
                                await edm(msg.author.id, e)
                                await dm(msg.author.id, public_address)
                                return
                        elif (privacy == "0"):
                            await ereply(msg, e)
                            await reply(msg, public_address)
                        return
                # BSC TOKENS
                elif ((coin == "busd")):
                    if (await has_wallet(msg.author.id, "bnb") == True):
                        data = await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(msg.author.id))
                        uttcex_id = await udefs.udefs.get_uid(msg.author.id)
                        privacy = data[15]
                        data = await sql_select(wallet_db["bnb"], "bnb", "key_name", uttcex_id)
                        public_address = data[0]
                        e = discord.Embed(title=f"Your {coin.upper()} Wallet", description=f"```\n{public_address}```",
                                          color=coincolor[coin])
                        if (privacy == "1"):
                            if (msg.guild is not None):
                                await edm(msg.author.id, e)
                                e = discord.Embed(title=f"A DM was sent to you.",
                                                  description=f"A DM containing your wallet details was sent to you.",
                                                  color=coincolor[coin])
                                await ereply(msg, e)
                                await dm(msg.author.id, public_address)
                                return
                            else:
                                await edm(msg.author.id, e)
                                await dm(msg.author.id, public_address)
                                return
                        elif (privacy == "0"):
                            await ereply(msg, e)
                            await reply(msg, public_address)
                        return
                elif (coin == "xrp"):
                    if (await has_wallet(msg.author.id, coin) == True):
                        data = await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(msg.author.id))
                        uttcex_id = await udefs.udefs.get_uid(msg.author.id)
                        privacy = data[15]
                        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
                        public_address = data[0]
                        e = discord.Embed(title=f"Your {coin.upper()} Wallet", description=f"```\n{public_address}```",
                                          color=coincolor[coin])
                        if (privacy == "1"):
                            if (msg.guild is not None):
                                await edm(msg.author.id, e)
                                e = discord.Embed(title=f"A DM was sent to you.",
                                                  description=f"A DM containing your wallet details was sent to you.",
                                                  color=coincolor[coin])
                                await ereply(msg, e)
                                await dm(msg.author.id, public_address)
                                return
                            else:
                                await edm(msg.author.id, e)
                                await dm(msg.author.id, public_address)
                                return
                        elif (privacy == "0"):
                            await ereply(msg, e)
                            await reply(msg, public_address)
                        return
                elif (coin == "sol"):
                    if (await has_wallet(msg.author.id, coin) == True):
                        data = await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(msg.author.id))
                        uttcex_id = await udefs.udefs.get_uid(msg.author.id)
                        # Update the SOL address list with this address and time
                        # Refresh if existing, expires in one hour if not refreshed
                        user_addy = await udefs.udefs.get_sol_address_from_uid(uttcex_id)
                        if len(sol_address_list) == 0:
                            pass
                        else:
                            for addy in sol_address_list:  # Addy will be a list object [address, time.time()] format
                                if addy[0] == user_addy:
                                    if addy[1] + 3600 < time.time():  # If not expired, do nothing
                                        pass
                                if addy[1] + 3600 > time.time():  # Delete if expired
                                    sol_address_list.remove(addy)
                                    sol_address_list.append([addy[0], time.time()])  # Update
                        sol_address_list.append([user_addy, time.time()])  # Update
                        privacy = data[15]
                        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
                        public_address = data[0]
                        payload = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "getMinimumBalanceForRentExemption",
                            "params": [0]  # Parameter 0 gets the rent information
                        }
                        try:
                            response = requests.post(udefs.coindefs.sol_url, json=payload).json()
                            exempt_lamports = Decimal(response["result"])
                            qual_string = ["> * Your address meets the minimum rent requirement.",
                                           "> * Minimum rent not met. Address subject to deletion.\n> Please deposit the minimum rent."]
                        except:
                            qual_string = "> * Minimum rent for exemption could not be calculated."
                        exempt_lamports = Decimal(response["result"])
                        exempt = await from_atomic(coin, exempt_lamports)
                        sol_val = await get_price(coin)
                        exempt_val = format(sol_val * exempt, ".2f")
                        bal = await udefs.coindefs.get_backend_wallet_balance_from_uid(uttcex_id, coin)
                        bal = await from_atomic(coin, bal)
                        if len(qual_string) == 2:
                            if bal < exempt:
                                qual_string = qual_string[1]
                            elif bal >= exempt:
                                qual_string = qual_string[0]
                        e = discord.Embed(title=f"Your {coin.upper()} Wallet", description=f"**Notice:** Solana requires rent for account storage.\n> * Minimum for rent exemption: **{exempt} {emojis[coin]} = ${exempt_val} USD**\n\n{qual_string}\n\n`{public_address}`", color=coincolor[coin])
                        if (privacy == "1"):
                            if (msg.guild is not None):
                                await edm(msg.author.id, e)
                                e = discord.Embed(title=f"A DM was sent to you.",
                                                  description=f"A DM containing your wallet details was sent to you.",
                                                  color=coincolor[coin])
                                await ereply(msg, e)
                                await dm(msg.author.id, public_address)
                                return
                            else:
                                await edm(msg.author.id, e)
                                await dm(msg.author.id, public_address)
                                return
                        elif (privacy == "0"):
                            await ereply(msg, e)
                            await reply(msg, public_address)
                        return
                elif (coin == "fluffy"):
                    if (await has_wallet(msg.author.id, coin) == True):
                        data = await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(msg.author.id))
                        uttcex_id = await udefs.udefs.get_uid(msg.author.id)
                        # Update the SOL address list with this address and time
                        # Refresh if existing, expires in one hour if not refreshed
                        user_addy = await udefs.udefs.get_sol_address_from_uid(uttcex_id)
                        if len(sol_address_list) == 0:
                            pass
                        else:
                            for addy in sol_address_list:  # Addy will be a list object [address, time.time()] format
                                if addy[0] == user_addy:
                                    if addy[1] + 3600 < time.time():  # If not expired, do nothing
                                        pass
                                if addy[1] + 3600 > time.time():  # Delete if expired
                                    sol_address_list.remove(addy)
                                    sol_address_list.append([addy[0], time.time()])  # Update
                        sol_address_list.append([user_addy, time.time()])  # Update
                        privacy = data[15]
                        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
                        public_address = data[0]
                        payload = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "getMinimumBalanceForRentExemption",
                            "params": [0]  # Parameter 0 gets the rent information
                        }
                        try:
                            response = requests.post(udefs.coindefs.sol_url, json=payload).json()
                            exempt_lamports = Decimal(response["result"])
                            qual_string = ["> * Your address meets the minimum rent requirement.",
                                           "> * Minimum rent not met. Address subject to deletion.\n> Please deposit the minimum rent."]
                        except:
                            qual_string = "> * Minimum rent for exemption could not be calculated."
                        exempt_lamports = Decimal(response["result"])
                        exempt = await from_atomic(coin, exempt_lamports)
                        sol_val = await get_price('sol')
                        exempt_val = format(sol_val * exempt, ".2f")
                        bal = await udefs.coindefs.get_backend_wallet_balance_from_uid(uttcex_id, coin)
                        bal = await from_atomic(coin, bal)
                        if len(qual_string) == 2:
                            if bal < exempt:
                                qual_string = qual_string[1]
                            elif bal >= exempt:
                                qual_string = qual_string[0]
                        e = discord.Embed(title=f"Your {coin.upper()} Wallet", description=f"**Notice:** Solana requires rent for account storage.\n> * Minimum for rent exemption: **{exempt} {emojis['sol']} = ${exempt_val} USD**\n\n{qual_string}\n\n`{public_address}`", color=coincolor[coin])
                        if (privacy == "1"):
                            if (msg.guild is not None):
                                await edm(msg.author.id, e)
                                e = discord.Embed(title=f"A DM was sent to you.",
                                                  description=f"A DM containing your wallet details was sent to you.",
                                                  color=coincolor[coin])
                                await ereply(msg, e)
                                await dm(msg.author.id, public_address)
                                return
                            else:
                                await edm(msg.author.id, e)
                                await dm(msg.author.id, public_address)
                                return
                        elif (privacy == "0"):
                            await ereply(msg, e)
                            await reply(msg, public_address)
                        return
                    else:
                        e = Embed(title = "No token addresses.",
                                  description = "You have not received any tokens on SOL yet.\n\nA FLUFFY address will be created for you when you receive FLUFFY.",
                                  color = coincolor[coin])
                        await msg.reply(embed = e)
                        return                                  
            else:
                await err(6, [msg])
                return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


# Withdraw from internal wallet
async def withdraw(msg: discord.Message):
    global waenabled
    if waenabled == False:
        await err(6, [msg])
        return
    epc = 3
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    target = str(msg.author.id)
    match (len(p)):
        case (1):
            e = discord.Embed(title="Command: u.withdraw",
                              description="**Usage:**\n`u.withdraw` `{amount}` `{coin}` `{address}`\n\nYou must type whole coin amounts like 0.501 XMR, not 300k piconero.", color=0xffffff)
            await ereply(msg, e)
            return
        case (4):
            if (waenabled == True):
                coin = p[2].lower()
                tmp = coin
                uttcex_id = await udefs.udefs.get_uid(target)
                if (alias[coin] not in (await get_coin_list())):
                    await err(17, [msg])
                    return
                amount = Decimal(p[1])
                address = p[3]
                coin = alias[coin]
                if coin in udefs.coindefs.bitcoinlib_coin_list:
                    # REMOVE WHEN COMPLETE
                    if msg.author.id not in admin_list:
                        await msg.reply("Bitcoin, Litecoin, and Doge wallet withdraws are under maintenance.\nPlease try later. We apologize for any inconvenience caused.\nYou may request a manual withdraw by contacting support.")
                        return
                    # REMOVE WHEN COMPLETE
                    if (await has_wallet(target, coin) == True):
                        if tmp in atomnames:
                            amount = await from_atomic(coin, amount)
                        data = await sql_select("uttcex_bot_db", "profiles", "discord_id", target)
                        e = discord.Embed(title=f"{emojis[coin]} Preparing your transaction ...",
                                          description="This message will update with information about\nyour transaction momentarily. ...",
                                          color=0xaaaa00)
                        m = await msg.reply(embed=e)
                        # First find a backend wallet with sufficient balance
                        back_address = ""
                        back_key = ""
                        back_bal = Decimal("0.0")
                        data = await sql_select(wallet_db[coin], coin, "*", "*")
                        for wallet in data: # Search for wallet with sufficient balance
                            data = await sql_select("mainnet", f"{coin}_utxos", "*", "*")
                            tmpd = None
                            for x in data:
                                back_bal += Decimal(x[3])
                                tmpd = x
                            back_bal = await from_atomic(coin, int(back_bal))
                            if amount < back_bal and wallet[3] == tmpd[2]:
                                back_address = wallet[0]
                                back_key = wallet[1]
                                break
                        print(len(back_key))
                        xuid = await udefs.udefs.get_uid_from_coin_address(coin, back_address)
                        # Then we estimate the TX fee
                        data = await sql_select(wallet_db[coin], coin, "key_name", xuid)
                        hdk = bitcoinlib.keys.HDKey.from_wif(back_key)
                        w = bitcoinlib.wallets.Wallet(uwallet[coin])
                        e = discord.Embed(title=f"{emojis[coin]} Preparing your transaction ...",
                                          description="This message will update with information about\nyour transaction momentarily.\n\nChecking service provider ...",
                                          color=0xaaaa00)
                        await m.edit(embed=e)
                        try:
                            w.balance_update_from_serviceprovider()
                        except bitcoinlib.wallets.WalletError as why:
                            e = discord.Embed(title=f"{emojis[coin]} Transaction Failed",
                                              description=f"{emojis[coin]} This transaction failed to send.\n```\n{why}```",
                                              color=0x990000)
                            await m.edit(embed=e)
                            return
                        e = discord.Embed(title=f"{emojis[coin]} Preparing your transaction ...",
                                          description="This message will update with information about\nyour transaction momentarily.\n\nUpdating wallet ...",
                                          color=0xaaaa00)
                        await m.edit(embed=e)
                        try:
                            w.utxos_update()
                        except bitcoinlib.wallets.WalletError as why:
                            e = discord.Embed(title=f"{emojis[coin]} Transaction Failed",
                                              description=f"{emojis[coin]} This transaction failed to send.\n```\n{why}```",
                                              color=0x990000)
                            await m.edit(embed=e)
                            return
                        try:
                            tx = w.transaction_create([(f"{address}", int(await to_atomic(amount, coin)))])
                        except bitcoinlib.wallets.WalletError as why:
                            e = discord.Embed(title=f"{emojis[coin]} Transaction Failed",
                                              description=f"{emojis[coin]} Failed to create transaction.\n```\n{why}```",
                                              color=0x990000)
                            await m.edit(embed=e)
                            return
                        fee = int(tx.calculate_fee())
                        xfee = await from_atomic(coin, fee)
                        print(f"Fee atomic: {fee}")
                        print(f"Fee whole: {xfee}")
                        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
                        bal = Decimal(data[7])
                        xtotal = Decimal(format(amount + xfee, decidic[coin]))
                        xtotal_atomic = int(await to_atomic(coin, xtotal))
                        if xtotal > bal:
                            await msg.reply(f"{emojis[coin]} Insufficient balance to withdraw.")
                            e = discord.Embed(title="Cancelled.", description=f"{emojis[coin]} Operation cancelled by system.",
                                              color=0x000000)
                            await m.edit(embed=e)
                            return
                        try:
                            tx.sign(keys=hdk)
                        except bitcoinlib.wallets.WalletError as why:
                            e = discord.Embed(title=f"{emojis[coin]} Transaction Failed",
                                              description=f"{emojis[coin]} This transaction failed to send.\n```\n{why}```",
                                              color=0x990000)
                            await m.edit(embed=e)
                            return
                        amount = Decimal(format(amount, decidic[coin]))
                        xfee = Decimal(format(xfee, decidic[coin]))
                        e = Embed(title=f"{emojis[coin]} Transaction Estimation", description=f"Fee: **{xfee}** {emojis[coin]}\n\nRecipient:\n`{address}`\n\nAmount to send: **{amount}**\n\nTotal to be spent: **{xtotal}** {emojis[coin]}\n\nIs this transaction acceptable?\n\n> * Type **\"yes\"** to confirm.\n> * Type **\"cancel\"** to cancel.\n\nYou have 15 seconds before this expires.", color=coincolor[coin])
                        await m.edit(embed=e)
                        def withdraw_confirm(msgx: discord.Message) -> bool:
                            return msgx.author.id == msg.author.id and msgx.channel.id == msg.channel.id and msgx.content.lower() in ["yes", "cancel"]
                        try:
                            reply = await client.wait_for("message", check=withdraw_confirm, timeout=15)
                        except asyncio.TimeoutError:
                            await m.edit(content="Your withdraw has timed out.")
                            return
                        if reply.content.lower() == "yes" and reply.author.id == msg.author.id:
                            # User confirmed, proceed with withdraw
                            e = Embed(title=f"{emojis[coin]} Transaction Estimation", description=f"Fee: **{xfee}** {emojis[coin]}\n\nRecipient:\n`{address}`\n\nAmount to send: **{amount}**\n\nTotal to be spent: **{xtotal}** {emojis[coin]}\n\n**Sending ...**", color=coincolor[coin])
                            await m.edit(embed=e)
                            pass
                        elif reply.content.lower() == "cancel" and reply.author.id == msg.author.id:
                            await m.edit(content="Withdraw cancelled.", embed=None)
                            return
                        try:
                            tx.send()
                        except:
                            e = discord.Embed(title=f"{emojis[coin]} Transaction Failed.",
                                              description=f"{emojis[coin]} This transaction failed to send.", color=0x990000)
                            await m.edit(embed=e)
                            return
                        # Create the NEGATIVE TX in the DB
                        # Note - DO: acknowledge  negative records for discrepancy check to balance the books
                        # Note - DO NOT: acknowledge negative TX records in DB in event of deposit detected!
                        txid = tx.txid
                        print(txid)
                        return
                        await sql_do("mainnet", f"INSERT INTO `{coin}_utxos` (tx_hash, receiving_address, sat_amount, credited) VALUES ('{txid}', '{address}', '-{xtotal_atomic}', '{1}');")
                        await sql_update("mainnet", f"{coin}_utxos", "io_flag", f"1", "receiving_address", f"{back_address}")
                        # Subtract the sender user instant balance
                        await swap_debit(msg.author.id, coin, xtotal)
                        e = discord.Embed(title="Sent!", description=f"Your {amount} {emojis[coin]} was sent to:\n```\n{address}```\n\nFee paid: **{xfee}** {emojis[coin]}\n\nTotal spent: **{xtotal}** {emojis[coin]}", color=0x00ff00)
                        await m.edit(embed = e)
                        return
                # WEB3 SMART CHAINS
                elif coin in udefs.coindefs.web3_coin_list:
                    if (await has_wallet(target, coin) == True):
                        # REMOVE WHEN COMPLETE
                        wkey = await udefs.udefs.get_key_from_uid(uttcex_id, coin)
                        waddy = await udefs.udefs.get_address_from_uid(uttcex_id, coin)
                        bal = await udefs.coindefs.get_instant_wallet_balance_from_uid(uttcex_id, coin)
                        amount = Decimal(amount)
                        e = discord.Embed(title=f"{emojis[coin]} Preparing your transaction ...",
                                          description="This message will update with information about\nyour transaction momentarily. ...",
                                          color=0xaaaa00)
                        m = await msg.reply(embed=e)
                        if amount > bal:
                            await msg.reply(f"{emojis[coin]} Insufficient balance to withdraw.")
                            e = discord.Embed(title="Cancelled.", description=f"{emojis[coin]} Operation cancelled by system.",
                                              color=0x000000)
                            await m.edit(embed=e)
                            return
                        if address == waddy:
                            await msg.reply(f"{emojis[coin]} Cannot withdraw to self.")
                            e = discord.Embed(title="Cancelled.", description=f"{emojis[coin]} Operation cancelled by system.",
                                              color=0x000000)
                            await m.edit(embed=e)
                            return
                        # Do withdraw - send test TX, then ask user to confirm
                        if coin == "eth" or coin in udefs.coindefs.evm_token_list:
                            amount_to_send = udefs.coindefs.evm_client.to_wei(amount, "ether")
                            gas_price = udefs.coindefs.evm_client.eth.gas_price
                        elif coin == "bnb" or coin in udefs.coindefs.bsc_token_list:
                            amount_to_send = udefs.coindefs.bsc_client.to_wei(amount, "ether")
                            gas_price = udefs.coindefs.bsc_client.eth.gas_price
                        elif coin == "matic" or coin in udefs.coindefs.matic_token_list:
                            amount_to_send = udefs.coindefs.matic_client.to_wei(amount, "ether")
                            gas_price = udefs.coindefs.matic_client.eth.gas_price
                        tx_params = {
                            'to': address,
                            'value': amount_to_send,
                            'gasPrice': gas_price,
                        }
                        if coin == "eth" or coin in udefs.coindefs.evm_token_list:
                            try:
                                gas_estimate = udefs.coindefs.evm_client.eth.estimate_gas(tx_params)
                            except web3.exceptions.InvalidAddress as e:
                                e = Embed(title = "Transaction Failed.",
                                          description = f"Error: {e}",
                                          color = 0xff0000)
                                await m.edit(embed = e)
                                return
                        elif coin == "bnb" or coin in udefs.coindefs.bsc_token_list:
                            try:
                                gas_estimate = udefs.coindefs.bsc_client.eth.estimate_gas(tx_params)
                            except web3.exceptions.InvalidAddress as e:
                                e = Embed(title = "Transaction Failed.",
                                          description = f"Error: {e}",
                                          color = 0xff0000)
                                await m.edit(embed = e)
                                return
                        elif coin == "matic" or coin in udefs.coindefs.matic_token_list:
                            try:
                                gas_estimate = udefs.coindefs.matic_client.eth.estimate_gas(tx_params)
                            except web3.exceptions.InvalidAddress as e:
                                e = Embed(title = "Transaction Failed.",
                                          description = f"Error: {e}",
                                          color = 0xff0000)
                                await m.edit(embed = e)
                                return
                        fee = int(gas_estimate) * (gas_price)
                        xgas_price = await from_atomic(coin, Decimal(gas_price))
                        xgas_estimate = await from_atomic(coin, Decimal(gas_estimate))
                        xfee = await from_atomic(coin, Decimal(fee))
                        xtotal = Decimal(await from_atomic(coin, fee + amount_to_send))

                        back_address = ""
                        back_key = ""
                        back_bal = Decimal("0.0")
                        data = await sql_select(wallet_db[coin], coin, "*", "*")
                        for wallet in data: # Search for wallet with sufficient balance
                            back_bal = await udefs.coindefs.get_backend_wallet_balance_from_address(wallet[0], coin)
                            if xtotal < back_bal:
                                back_address = wallet[0]
                                back_key = wallet[1]
                                break
                        wx = None
                        if coin == "eth" or coin in udefs.coindefs.web3_coin_list:
                            wx = udefs.coindefs.evm_client.eth.account.from_key(back_key)
                        elif coin == "bnb" or coin in udefs.coindefs.evm_token_list:
                            wx = udefs.coindefs.bsc_client.eth.account.from_key(back_key)
                        elif coin == "matic" or coin in udefs.coindefs.bsc_token_list:
                            wx = udefs.coindefs.matic_client.eth.account.from_key(back_key)
                        # Test if the backend can afford the amount + fee
                        if xtotal > back_bal:
                            await msg.reply(f"{emojis[coin]} There was an internal error while creating this transaction.\n\nPlease try again later.")
                            e = discord.Embed(title="Cancelled.", description=f"{emojis[coin]} Operation cancelled by system.",
                                              color=0x000000)
                            await m.edit(embed=e)
                            return
                        # Test if they can afford the amount + fee
                        if xtotal > bal:
                            await msg.reply(f"{emojis[coin]} Insufficient balance to withdraw.\n\nGas estimate: **{format(xgas_estimate, decidic[coin])}** {emojis[coin]}\nGas price: **{format(xgas_price, decidic[coin])}** {emojis[coin]}\nFee: **{format(xfee, decidic[coin])}** {emojis[coin]}\n\nTotal cost: **{amount + fee}** {emojis[coin]}\n\nYour balance: **{bal}** {emojis[coin]}")
                            e = discord.Embed(title="Cancelled.", description=f"{emojis[coin]} Operation cancelled by system.",
                                              color=0x000000)
                            await m.edit(embed=e)
                            return
                        e = Embed(title = f"{emojis[coin]} Transaction Estimation", description = f"Gas estimate: **{format(xgas_estimate, decidic[coin])}** {emojis[coin]}\nGas price: **{format(xgas_price, decidic[coin])}** {emojis[coin]}\nFee: **{format(xfee, decidic[coin])}** {emojis[coin]}\n\nRecipient:\n`{address}`\n\nTotal to be spent: **{xtotal}** {emojis[coin]}\n\nAmount to send: **{format(amount, decidic[coin])}** {emojis[coin]}\n\nIs this transaction acceptable?\n\n> * Type **\"yes\"** to confirm.\n> * Type **\"cancel\"** to cancel.\n\nYou have 15 seconds before this expires.", color = coincolor["eth"])
                        await m.edit(embed = e)
                        def withdraw_confirm(msgx: discord.Message) -> bool:
                            return msgx.author.id == msg.author.id and msgx.channel.id == msg.channel.id and msgx.content.lower() in ["yes", "cancel"]
                        try:
                            reply = await client.wait_for("message", check=withdraw_confirm, timeout=15)
                        except asyncio.TimeoutError:
                            await m.edit(content="Your withdraw has timed out.")
                            return
                        if reply.content.lower() == "yes" and reply.author.id == msg.author.id:
                            # User confirmed, proceed with withdraw
                            pass
                        elif reply.content.lower() == "cancel" and reply.author.id == msg.author.id:
                            await m.edit(content="Withdraw cancelled.", embed=None)
                            return
                        data = await sql_select("mainnet", f"{coin}_utxos", "receiving_address", back_address)
                        nonce = int(data[4])
                        tx_params = {
                            'to': address,
                            'from': back_address,
                            'value': amount_to_send,
                            'gas': gas_estimate,
                            'gasPrice': gas_price,
                            'nonce': nonce,
                            'chainId': udefs.coindefs.chain_ids[coin],  # Use chain ID for network
                        }
                        price = await get_price(coin)
                        val = xtotal * price
                        xtotal_atomic = await to_atomic(coin, xtotal)
                        if coin == "eth" or coin in udefs.coindefs.evm_token_list:
                            signed_tx = udefs.coindefs.evm_client.eth.account.sign_transaction(tx_params, back_key)
                            tx_hash = udefs.coindefs.evm_client.eth.send_raw_transaction(signed_tx.rawTransaction)
                        elif coin == "bnb" or coin in udefs.coindefs.bsc_token_list:
                            signed_tx = udefs.coindefs.matic_client.eth.account.sign_transaction(tx_params, back_key)
                            tx_hash = udefs.coindefs.matic_client.eth.send_raw_transaction(signed_tx.rawTransaction)
                        elif coin == "matic" or coin in udefs.coindefs.matic_token_list:
                            signed_tx = udefs.coindefs.matic_client.eth.account.sign_transaction(tx_params, back_key)
                            tx_hash = udefs.coindefs.matic_client.eth.send_raw_transaction(signed_tx.rawTransaction)
                        e = Embed(title="{emojis[coin]} Sent!", description=f"Sent **{amount}** {emojis[coin]}!")
                        # Create the NEGATIVE TX in the DB
                        # Note - DO: acknowledge  negative records for discrepancy check to balance the books
                        # Note - DO NOT: acknowledge negative TX records in DB in event of deposit detected!
                        await sql_do("mainnet", f"INSERT INTO `{coin}_utxos` (tx_hash, receiving_address, atom_amount, credited) VALUES ('{tx_hash.hex()}', '{address}', '-{xtotal_atomic}', '{1}');")
                        data = await sql_select("mainnet", f"{coin}_utxos", "receiving_address", back_address)
                        nonce = int(data[4]) + 1
                        await sql_update("mainnet", f"{coin}_utxos", "nonce", f"{nonce}", "receiving_address", f"{back_address}")
                        await sql_update("mainnet", f"{coin}_utxos", "io_flag", f"1", "receiving_address", f"{back_address}")
                        # Subtract the sender user instant balance
                        await swap_debit(msg.author.id, coin, xtotal)
                        e = discord.Embed(title="Sent!", description=f"Your {amount} {emojis[coin]} was sent to:\n```\n{address}```\n\nFee paid: **{xfee}** {emojis[coin]}\n\nTotal spent: **{xtotal}** {emojis[coin]}", color=0x00ff00)
                        await m.edit(embed = e)
                        return
                # EVM TOKENS
                elif coin in udefs.coindefs.evm_token_list:
                    # REMOVE WHEN COMPLETE
                    if coin == "usdt":
                        await msg.reply("USDT wallet withdraws are under maintenance.\nPlease try later. We apologize for any inconvenience caused.\nYou may request a manual withdraw by contacting support.")
                        return
                    # REMOVE WHEN COMPLETE
                    if (await has_wallet(target, coin) == True):
                        wkey = await udefs.udefs.get_key_from_uid(uttcex_id, coin)
                        waddy = await udefs.udefs.get_address_from_uid(uttcex_id, coin)
                        bal = await udefs.coindefs.get_instant_wallet_balance_from_uid(uttcex_id, coin)
                        amount = Decimal(amount)
                        e = discord.Embed(title=f"{emojis['eth']} {emojis[coin]} Preparing your transaction ...",
                                          description="This message will update with information about\nyour transaction momentarily. ...",
                                          color=0xaaaa00)
                        m = await msg.reply(embed=e)
                        if amount > bal:
                            await msg.reply(f"{emojis[coin]} Insufficient balance to withdraw.")
                            e = discord.Embed(title="Cancelled.", description=f"{emojis['eth']} {emojis[coin]} Operation cancelled by system.",
                                              color=0x000000)
                            await m.edit(embed=e)
                            return
                        if address == waddy:
                            await msg.reply(f"{emojis[coin]} Cannot withdraw to self.")
                            e = discord.Embed(title="Cancelled.", description=f"{emojis['eth']} {emojis[coin]} Operation cancelled by system.",
                                              color=0x000000)
                            await m.edit(embed=e)
                            return
                # BSC TOKENS
                elif coin in udefs.coindefs.bsc_token_list:
                    # REMOVE WHEN COMPLETE
                    if coin == "busd":
                        await msg.reply("BUSD wallet withdraws are under maintenance.\nPlease try later. We apologize for any inconvenience caused.\nYou may request a manual withdraw by contacting support.")
                        return
                    # REMOVE WHEN COMPLETE
                    if (await has_wallet(target, coin) == True):
                        wkey = await udefs.udefs.get_key_from_uid(uttcex_id, coin)
                        waddy = await udefs.udefs.get_address_from_uid(uttcex_id, coin)
                        bal = await udefs.coindefs.get_instant_wallet_balance_from_uid(uttcex_id, coin)
                        amount = Decimal(amount)
                        e = discord.Embed(title=f"{emojis['bnb']} {emojis[coin]} Preparing your transaction ...",
                                          description="This message will update with information about\nyour transaction momentarily. ...",
                                          color=0xaaaa00)
                        m = await msg.reply(embed=e)
                        if amount > bal:
                            await msg.reply(f"{emojis[coin]} Insufficient balance to withdraw.")
                            e = discord.Embed(title="Cancelled.", description=f"{emojis['bnb']} {emojis[coin]} Operation cancelled by system.",
                                              color=0x000000)
                            await m.edit(embed=e)
                            return
                        if address == waddy:
                            await msg.reply(f"{emojis[coin]} Cannot withdraw to self.")
                            e = discord.Embed(title="Cancelled.", description=f"{emojis['bnb']} {emojis[coin]} Operation cancelled by system.",
                                              color=0x000000)
                            await m.edit(embed=e)
                            return
                elif (coin == "xrp"):
                    if (await has_wallet(target, coin) == True):
                        data = await sql_select("uttcex_bot_db", "profiles", "discord_id", target)
                        if (float(amount) < atomdic[coin]):
                            await err(16, [msg])
                            return
                        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
                        bal = float(data[7])
                        if amount > bal:
                            await reply(msg, "Insufficient balance to withdraw.")
                            e = discord.Embed(title="Cancelled.", description="Operation cancelled by system.",
                                              color=0x000000)
                            await m.edit(embed=e)
                            return
                        wkey = data[1]
                        waddy = data[0]
                        w = xrpl.wallet.Wallet.from_seed(wkey)
                        url = {"server": "https://s1.ripple.com:51234/", "timeout": 10}
                        xrp_client = xrpl.clients.JsonRpcClient(url)
                        accinfo = xrpl.models.requests.account_info.AccountInfo(account=waddy)
                        r = xrp_client.request(accinfo)
                        ntx = xrpl.models.transactions.Payment(
                            account=waddy,
                            amount=str(await to_atomic(coin, amount)),
                            destination=address,
                            sequence=r.result["account_data"]["Sequence"]
                        )
                        stx = xrpl.transaction.sign_and_submit(ntx, xrp_client, w)
                        if stx.is_successful():
                            e = discord.Embed(title="Sent!",
                                              description=f"Your {format(await from_atomic(amount), decidic[coin])} {emojis[coin]} was sent to:\n```\n{address}```\n\n**Fee paid:** {fee} XRP.",
                                              color=0x00ff00)
                            await m.edit(embed=e)
                            return
                        else:
                            e = discord.Embed(title="Transaction Failed.",
                                              description=f"This transaction failed to send.", color=0x990000)
                            await m.edit(embed=e)
                            return
                elif (coin == "sol"):
                    # REMOVE WHEN COMPLETE
                    await msg.reply("SOL and FLUFFY wallet withdraws are under maintenance.\nPlease try later. We apologize for any inconvenience caused.\nYou may request a manual withdraw by contacting support.")
                    return
                    # REMOVE WHEN COMPLETE
                    if (await has_wallet(target, coin) == True):
                        if (float(amount) < atomdic[coin]):
                            await err(16, [msg])
                            return
                        data = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
                        pkey = data[1]
                        ac1 = solathon.Keypair().from_private_key(pkey)
                        ac2 = solathon.PublicKey(address)
                        bal = Decimal(data[5])
                        fee = Decimal(str(sol_client.get_fees()["value"]["feeCalculator"]["lamportsPerSignature"]))
                        fee = await from_atomic(coin, fee)
                        if Decimal(amount) + fee > bal:
                            await reply(msg, "Insufficient balance to withdraw.")
                            e = discord.Embed(title="Cancelled.", description="Operation cancelled by system.\n\n",
                                              color=0x000000)
                            await m.edit(embed=e)
                            return
                        e = discord.Embed(title="Preparing your transaction ...",
                                          description="This message will update with information about\nyour transaction momentarily. ...",
                                          color=0xaaaa00)
                        m = await msg.reply(embed=e)
                        instruction = solathon.core.instructions.transfer(
                            from_public_key=ac1.public_key,
                            to_public_key=ac2,
                            lamports=int(await to_atomic(coin, amount)),
                        )
                        tx = solathon.Transaction(instructions=[instruction], signers=[ac1])
                        tx.recent_blockhash = sol_client.get_recent_blockhash().blockhash
                        try:
                            tx.sign()
                        except:
                            e = discord.Embed(title = "Failed sign.")
                            await m.edit(embed = e)
                            return
                        try:
                            tx.serialize()
                        except:
                            e = discord.Embed(title = "Failed serialize.")
                            await m.edit(embed = e)
                            return
                        txid = None
                        try:
                            txid = sol_client.send_transaction(tx)
                        except:
                            e = discord.Embed(title = "Failed send.")
                            await m.edit(embed = e)
                            return
                        new_bal = bal - (await from_atomic(coin, amount)) - (await from_atomic(coin, fee))
                        await sql_update(wallet_db[coin], coin, "instant_balance", f"{new_bal}", "key_name", uttcex_id)
                        e = Embed(title=f"{emojis[coin]} Success!", description = f"Successfully sent {amount} {emojis[coin]} to address:\n```{address}```\nTransaction fee: {await from_atomic(coin, fee)} {emojis[coin]}\n\nTransaction hash:\n**{txid}**\n\nYour new {coin.upper()} balance:\n**{new_bal}** {emojis[coin]}", color = coincolor[coin])
                        await m.edit(embed = e)
                        return
            else:
                await err(6, [msg])
                return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def escrow_unlock(tid: str, oid: str, coin: str, amount: str):
    amount = format(Decimal(amount), decidic[coin])
    uttcex_id = await udefs.udefs.get_uid(tid)
    bal = 0
    if ((coin == "btc") or (coin == "ltc") or (coin == "doge")):
        try:
            bal = Decimal(await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)[7])
        except:
            bal = Decimal(0.0)
    elif ((coin == "eth") or (coin == "usdc") or (coin == "usdt") or (coin == "shib") or (coin == "pussy") or (
            coin == "matic") or (coin == "bnb") or (coin == "busd") or (coin == "cds") or (coin == "op") or (
                  coin == "avax")):
        try:
            bal = Decimal(await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)[5])
        except:
            bal = Decimal(0.0)
    elif ((coin == "sol") or (coin == "xrp")):
        try:
            bal = Decimal(await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)[5])
        except:
            bal = Decimal(0.0)
    elif ((coin == "fluffy")):
        try:
            bal = Decimal(await sql_select(wallet_db["sol"], "sol", "key_name", uttcex_id)[6])
        except:
            bal = Decimal(0.0)
    # Return to user
    new_bal = str(format(bal + Decimal(amount), decidic[coin]))
    await sql_update(wallet_db[coin], coin, "instant_balance", new_bal, "key_name", uttcex_id)
    await sql_do("uttcex_bot_db", f"DELETE FROM `locked_balance` WHERE `origin` = '{oid}' AND `coin` = '{coin}' AND `amount` = '{amount}';")
    return


async def escrow(msg: discord.Message):
    origin = str(msg.author.id)
    footer = "Escrow deposits will remain active until cancelled or completed."
    global esenabled
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    epc = 1
    match (len(p)):
        case (1):
            e = discord.Embed(title="Command: u.escrow",
                              description="**Usage:**\n`u.escrow` `{user}`\n\nInitiates an escrow between you and the target user.\n**Escrow is a __free__ service**.\n\n`u.escrow` `{amount}` `{coin}`\nType \"`u.escrow ?`\" to check your escrow information.\n\nType \"`u.escrow cancel`\" to immediately cancel the escrow.\n\nType \"`u.escrow confirm`\" to confirm your escrow.\nEscrow cannot be completed until both parties have used \"`u.escrow confirm`\".\n\nEither party may use \"`u.escrow complete`\" once confirmed.\n\nTo deposit coins into your escrow, use\n" + "```\nu.escrow deposit {amount} {coin}```",
                              color=0xffffff)
            e.set_footer(text=footer)
            await ereply(msg, e)
            return
        case (2):
            if (esenabled == True):
                pass
            else:
                e = discord.Embed(title="Escrow Disabled",
                                  description="Escrows are currently disabled and are under development.",
                                  color=0xffffff)
                await ereply(msg, e)
                return
            target = str(await stripid(p[1])).lower()
            match (target):
                case ("?"):
                    data = await sql_select("uttcex_bot_db", "escrows", "origin", origin)
                    try:
                        target = data[1]
                    except:
                        data = await sql_select("uttcex_bot_db", "escrows", "target", origin)
                        if (data is None):
                            e = discord.Embed(title="No Escrow Found",
                                              description="You are not currently in escrow with anyone.",
                                              color=0xff00ff)
                            e.set_footer(text=footer)
                            await ereply(msg, e)
                            return
                        target = data[0]
                    eid = data[2]
                    deposits = await sql_select("uttcex_escrows", eid, "*", "*")
                    ndeps = ""
                    if (deposits == None):
                        e = discord.Embed(title="Escrow Info",
                                          description=f"You are in escrow with: <@{target}>.\n\n**Your deposits:**\n```None.```",
                                          color=0xff00ff)
                        e.set_footer(text=footer)
                        await ereply(msg, e)
                        return
                    else:
                        for dep in deposits:
                            if dep[0] == origin:
                                coin = dep[1]
                                amount = dep[2]
                                ndeps += f"**{amount}** {emojis[coin]}\n"
                    e = discord.Embed(title="Escrow Info",
                                      description=f"You are in escrow with: <@{target}>.\n\n**Your deposits:**\n{ndeps}",
                                      color=0xff00ff)
                    e.set_footer(text=footer)
                    await ereply(msg, e)
                    return
                case ("cancel"):
                    data = None
                    try:
                        data = await sql_select("uttcex_bot_db", "escrows", "origin", origin)
                    except:
                        data = await sql_select("uttcex_bot_db", "escrows", "target", origin)
                    target = data[1]
                    if (data is None):
                        e = discord.Embed(title="No Escrow Found",
                                          description="You are not currently in escrow with anyone.", color=0xff00ff)
                        e.set_footer(text=footer)
                        await ereply(msg, e)
                        return
                    eid = data[2]
                    # Get user deposits
                    deposits = []
                    try:
                        deposits = await sql_select("uttcex_escrows", eid, "*", "*")
                    except:
                        await sql_do("uttcex_escrows", f"DROP TABLE {eid}")
                        await sql_delete("uttcex_bot_db", "escrows", "escrow_id", eid)
                        e = discord.Embed(title="Escrow Cancelled", description=f"You have cancelled your escrow.",
                                          color=0xff00ff)
                        e.set_footer(text=footer)
                        await ereply(msg, e)
                        return
                    origindeps = []
                    targetdeps = []
                    if (deposits == None):
                        await sql_do("uttcex_escrows", f"DROP TABLE {eid}")
                        await sql_delete("uttcex_bot_db", "escrows", "escrow_id", eid)
                        e = discord.Embed(title="Escrow Cancelled", description=f"You have cancelled your escrow.",
                                          color=0xff00ff)
                        e.set_footer(text=footer)
                        await ereply(msg, e)
                        return
                    for dep in deposits:
                        if dep[0] == origin:
                            coin = dep[1]
                            amount = Decimal(dep[2])
                            origindeps.append([coin, amount])
                        elif dep[0] == target:
                            coin = dep[1]
                            amount = Decimal(dep[2])
                            origindeps.append([coin, amount])
                    for dep in origindeps:
                        await unlock_bal("", origin, dep[0], dep[1])
                    for dep in targetdeps:
                        await unlock_bal("", target, dep[0], dep[1])
                    await sql_do("uttcex_bot_db", f"DELETE FROM `escrows` WHERE `escrow_id` = '{eid}'")
                    await sql_do("uttcex_escrows", f"DROP TABLE `{eid}`")
                    e = discord.Embed(title="Escrow Cancelled", description=f"Deposits have been returned.\nThe escrow `{eid}` between <@{origin}> and <@{target}> has been cancelled.",
                                      color=0xff00ff)
                    e.set_footer(text=footer)
                    await ereply(msg, e)
                    return
                case ("confirm"):
                    eid = None
                    data = await sql_select("uttcex_bot_db", "escrows", "origin", origin)
                    if (data is None):
                        data = await sql_select("uttcex_bot_db", "escrows", "target", origin)
                    if (data is None):
                        e = discord.Embed(title="No Escrow Found",
                                          description="You are not currently in escrow with anyone.", color=0xff00ff)
                        e.set_footer(text=footer)
                        await ereply(msg, e)
                        return
                    eid = data[2]
                    origin = data[0]
                    target = data[1]
                    if (int(msg.author.id) == int(origin)):
                        await sql_update("uttcex_bot_db", "escrows", "origin_confirm", "1", "escrow_id", eid)
                        e = discord.Embed(title="Escrow Confirmed",
                                          description=f"<@{origin}>, your escrow was confirmed.\n\nYou may still cancel even if <@{target}> has not confirmed.\n\nTo finalize, use \"`u.escrow complete`\".",
                                          color=0xff00ff)
                        e.set_footer(text=footer)
                        await ereply(msg, e)
                        return
                    elif (int(msg.author.id) == int(target)):
                        await sql_update("uttcex_bot_db", "escrows", "target_confirm", "1", "escrow_id", eid)
                        e = discord.Embed(title="Escrow Confirmed",
                                          description=f"<@{target}>, your escrow was confirmed.\n\nYou may still cancel even if <@{origin}> has not confirmed.\n\nTo finalize, use \"`u.escrow complete`\".",
                                          color=0xff00ff)
                        e.set_footer(text=footer)
                        await ereply(msg, e)
                        return
                case ("complete"):
                    eid = None
                    data = await sql_select("uttcex_bot_db", "escrows", "origin", origin)
                    if (data is None):
                        data = await sql_select("uttcex_bot_db", "escrows", "target", origin)
                    eid = data[2]
                    origin = data[0]
                    target = data[1]
                    oc = data[3]
                    tc = data[4]
                    if ((oc == "1") and (tc == "1")):
                        # Get user deposits
                        deposits = await sql_select("uttcex_escrows", eid, "*", "*")
                        origindeps = []
                        targetdeps = []
                        for dep in deposits:
                            if dep[0] == origin:
                                coin = dep[1]
                                amount = Decimal(dep[2])
                                origindeps.append([coin, amount])
                            elif dep[0] == target:
                                coin = dep[1]
                                amount = Decimal(dep[2])
                                targetdeps.append([coin, amount])
                        for dep in origindeps:
                            await escrow_unlock(target, origin, dep[0], dep[1])
                        for dep in targetdeps:
                            await escrow_unlock(origin, target, dep[0], dep[1])
                        await sql_do("uttcex_escrows", f"DROP TABLE {eid}")
                        await sql_delete("uttcex_bot_db", "escrows", "escrow_id", eid)
                        e = discord.Embed(title="Escrow Complete",
                                          description=f"The escrow between <@{origin}> and <@{target}> has completed successfully.",
                                          color=0xff00ff)
                        e,set_footer(text=footer)
                        await ereply(msg, e)
                        return
                    else:
                        if ((oc == "1") and (tc == "0")):
                            if (int(msg.author.id) == int(origin)):
                                e = discord.Embed(title="Awaiting Confirmation",
                                                  description=f"This escrow is still pending until <@{target}> confirms.",
                                                  color=0xff00ff)
                                await ereply(msg, e)
                                return
                            elif (int(msg.author.id) == int(target)):
                                e = discord.Embed(title="Awaiting Confirmation",
                                                  description=f"This escrow is still pending until you confirm.",
                                                  color=0xff00ff)
                                await ereply(msg, e)
                                return
                        elif ((oc == "0") and (tc == "1")):
                            if (int(msg.author.id) == int(target)):
                                e = discord.Embed(title="Awaiting Confirmation",
                                                  description=f"This escrow is still pending until <@{origin}> confirms.",
                                                  color=0xff00ff)
                                await ereply(msg, e)
                                return
                            elif (int(msg.author.id) == int(origin)):
                                e = discord.Embed(title="Awaiting Confirmation",
                                                  description=f"This escrow is still pending until you confirm.",
                                                  color=0xff00ff)
                                await ereply(msg, e)
                                return
                case _:  # ID specified - create a new escrow
                    if (int(origin) == int(target)):
                        await err(-1, [msg, "Cannot initiate an escrow with yourself."])
                        return
                    elif (int(target) == bot_ids[BOT_CFG_FLAG]["uttcex"]): #bot_ids[BOT_CFG_FLAG]["uttcex"]
                        await err(-1, [msg, "Cannot initiate an escrow with UTTCex directly."])
                        return
                    elif ((await is_banned(target)) == True):
                        await err(-1, [msg, "Cannot initiate an escrow with a banned user."])
                        return
                    datax = await sql_select("uttcex_bot_db", "escrows", "origin", origin)
                    datay = await sql_select("uttcex_bot_db", "escrows", "target", origin)
                    if ((datax is not None) or (datay is not None)):
                        await err(-1, [msg, "Cannot initiate more than 1 escrow at a time."])
                        return
                    # Create the escrow
                    await sql_insert("uttcex_bot_db", "escrows", "origin", origin)
                    await sql_update("uttcex_bot_db", "escrows", "target", target, "origin", origin)
                    eid = await rstr(10, 1)
                    await sql_update("uttcex_bot_db", "escrows", "escrow_id", eid, "origin", origin)
                    await sql_do("uttcex_escrows", f"CREATE TABLE {eid} (`origin` VARCHAR(19), `coin` VARCHAR(11), `amount` VARCHAR(64));")
                    e = discord.Embed(title="Escrow Initiated!",
                                      description=f"You have engaged in escrow with <@{target}>!\n\n" + "To deposit into this escrow, use the `deposit` parameter:\n```u.escrow deposit {amount} {coin}```",
                                      color=0xff00ff)
                    e.set_footer(text=footer)
                    await ereply(msg, e)
                    return
        case (4): # Deposits
            target = p[1]
            amount = p[2]
            coin = p[3]
            if target.lower() == "deposit":
                data = await sql_select("uttcex_bot_db", "escrows", "origin", origin)
                if (data == None):
                    data = await sql_select("uttcex_bot_db", "escrows", "target", origin)
                    if (data == None):
                        e = discord.Embed(title="Error",
                                          description="You are not engaged in escrow and have nowhere to deposit.",
                                          color=0xff0000)
                        await ereply(msg, e)
                        return
                eid = data[2]
                if (coin in atomnames):  # This is an atomic tip
                    coin = alias[coin]
                    amount = format(await from_atomic(coin, amount), decidic[coin])
                else:
                    amount = format(Decimal(amount), decidic[coin])
                await lock_bal("", origin, coin, amount)
                await sql_do("uttcex_escrows",
                             f"INSERT INTO `{eid}` (`origin`, `coin`, `amount`) VALUES ('{origin}','{coin}','{amount}')")
                e = discord.Embed(title="Escrow", description=f"You have deposited **{amount}** {emojis[coin]}",
                                  color=0xff00ff)
                e.set_footer(text=footer)
                await ereply(msg, e)
                return
            else:
                return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def testswap(msg: discord.Message):
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    epc = 3
    match (len(p)):
        case (4):
            amount = p[1]
            incoin = p[2]
            tmp = incoin
            outcoin = p[3]
            try:
                incoin = alias[incoin]
            except:
                await err(17, [msg])
                return
            try:
                outcoin = alias[outcoin]
            except:
                await err(17, [msg])
                return
            if incoin == outcoin:
                await err(-1, [msg, "Same-coin recursive swaps not enabled.\nSpecial secret feature in development."])
                return
            inprice = Decimal(format(await get_price(incoin), '.8f'))
            outprice = Decimal(format(await get_price(outcoin), '.8f'))
            inrate = rate_dic[incoin]
            rate = rate_dic[outcoin]
            uttcex_id = await udefs.udefs.get_uid(msg.author.id)
            discount = Decimal((await sql_select("uttcex_bot_db", "profiles", "uttcex_id", uttcex_id))[15])
            if (discount != Decimal(0.0)):
                discount = Decimal(format(discount / 100, '.2f'))
            palette = 0x00ffbf
            if inrate == rate:
                rate = Decimal("0.98")
            elif inrate < rate:
                rate = inrate
                palette = coincolor[incoin]
            if (amount.find("$") == -1):  # Dollar sign not found
                amount = Decimal(amount)
                if (tmp in atomnames):
                    amount = Decimal(format(await from_atomic(incoin, amount), decidic[incoin]))
                invalue = Decimal(format(inprice * amount, '.8f'))
                outvalue = Decimal(format(invalue * rate, '.8f'))
                outamount = Decimal(format(outvalue / outprice, decidic[outcoin]))
                fee = invalue - outvalue
                feeamount = Decimal(format(fee / outprice, decidic[outcoin]))
                outamount = Decimal(format((outvalue / outprice) - feeamount, decidic[outcoin]))
                feepct = int((1 - rate) * 100)
                e = discord.Embed(title="Use this to test swaps.",
                                  description="Coins of equal rating will have a default 2% fee.", color=palette)
                e.set_author(name="Test Swap",
                             icon_url="https://media.discordapp.net/attachments/849759474868158504/1242229345846690012/image.png")
                e.add_field(name="Input Coin:",
                            value=f"{emojis[incoin]} __`{format(amount, decidic[incoin])}`__\nRate: **({inrate})**",
                            inline=True)
                e.add_field(name="Output Coin:",
                            value=f"{emojis[outcoin]} __`{format(outamount, decidic[outcoin])}`__\nRate: **({rate_dic[outcoin]})**",
                            inline=True)
                e.add_field(name="Fee Incurred:",
                            value=f"{emojis[outcoin]} __`{format(feeamount, decidic[outcoin])}`__\n**({emojis[outcoin]} ${fee})**\n**({feepct}%) ({rate})**",
                            inline=True)
                e.add_field(name="Input Value:", value=f"{emojis[incoin]} ${invalue}", inline=True)
                e.add_field(name="Output Value:", value=f"{emojis[outcoin]} ${outvalue}", inline=True)
                e.add_field(name="Discount:", value=f"**{int(discount * 100)}%**", inline=True)
                if (outamount < atomdic[outcoin]):
                    e.add_field(name="Notice:",
                                value=f"The output coin is too small.\n(`< {format(atomdic[outcoin], decidic[outcoin])}`)\nThis trade will fail.",
                                inline=True)
                    e.color = 0xff0000
                if (feeamount < atomdic[outcoin]):
                    e.add_field(name="Notice:",
                                value=f"No fee could be collected.\n(`< {format(atomdic[outcoin], decidic[outcoin])}`)\nThis trade will fail.",
                                inline=True)
                    e.color = 0xff0000
                e.set_footer(
                    text="Prices powered by CoinGecko. UTTCex powered by Father Crypto and the UTTCex development team.")
                await ereply(msg, e)
                return
            elif (amount.find("$") != -1):  # Dollar sign found
                value = Decimal(format(Decimal(await get_price(incoin)), decidic[incoin]))
                amount = Decimal(amount.replace("$", ""))
                amount = Decimal(format(amount / value, decidic[incoin]))
                if (tmp in atomnames):
                    amount = Decimal(format(await from_atomic(incoin, amount), decidic[incoin]))
                invalue = Decimal(format(inprice * amount, '.8f'))
                outvalue = Decimal(format(invalue * rate, '.8f'))
                outamount = Decimal(format(outvalue / outprice, decidic[outcoin]))
                fee = invalue - outvalue
                feeamount = Decimal(format(fee / outprice, decidic[outcoin]))
                outamount = Decimal(format((outvalue / outprice) - feeamount, decidic[outcoin]))
                feepct = int((1 - rate) * 100)
                e = discord.Embed(title="Use this to test swaps.",
                                  description="Coins of equal rating will have a default 2% fee.", color=palette)
                e.set_author(name="Test Swap",
                             icon_url="https://media.discordapp.net/attachments/849759474868158504/1242229345846690012/image.png")
                e.add_field(name="Input Coin:",
                            value=f"{emojis[incoin]} __`{format(amount, decidic[incoin])}`__\nRate: **({inrate})**",
                            inline=True)
                e.add_field(name="Output Coin:",
                            value=f"{emojis[outcoin]} __`{format(outamount, decidic[outcoin])}`__\nRate: **({rate_dic[outcoin]})**",
                            inline=True)
                e.add_field(name="Fee Incurred:",
                            value=f"{emojis[outcoin]} __`{format(feeamount, decidic[outcoin])}`__\n**({emojis[outcoin]} ${fee})**\n**({feepct}%) ({rate})**",
                            inline=True)
                e.add_field(name="Input Value:", value=f"{emojis[incoin]} ${invalue}", inline=True)
                e.add_field(name="Output Value:", value=f"{emojis[outcoin]} ${outvalue}", inline=True)
                e.add_field(name="Discount:", value=f"**{int(discount * 100)}%**", inline=True)
                if (outamount < atomdic[outcoin]):
                    e.add_field(name="Notice:",
                                value=f"The output coin is too small.\n(`< {format(atomdic[outcoin], decidic[outcoin])}`)\nThis trade will fail.",
                                inline=True)
                    e.color = 0xff0000
                if (feeamount < atomdic[outcoin]):
                    e.add_field(name="Notice:",
                                value=f"No fee could be collected.\n(`< {format(atomdic[outcoin], decidic[outcoin])}`)\nThis trade will fail.",
                                inline=True)
                    e.color = 0xff0000
                e.set_footer(
                    text="Prices powered by CoinGecko. UTTCex powered by Father Crypto and the UTTCex development team.")
                await ereply(msg, e)
                return
        case _:
            await err(2, [msg,
                          msg.content + "`\n\nExpected format:\n`u.testswap` `{amount}` `coin 1` `coin 2`\n\nYou may use dollar ($) amounts as well",
                          epc, pg])
            return


async def swap_credit(tid, coin: str, amount: Decimal):
    if (await has_profile(tid) == True):  # Sanity check 1
        pass
    if (await has_wallet(tid, coin) == True):  # Sanity check 2
        pass
    uttcex_id = await udefs.udefs.get_uid(tid)
    old_bal = 0
    # BITCOINLIB
    if ((coin == "btc") or (coin == "ltc") or (coin == "doge")):
        old_bal = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
        old_bal = old_bal[7]
        if old_bal == "":
            old_bal = Decimal("0.0")
        else:
            old_bal = Decimal(old_bal)
    # WEB3
    elif ((coin == "eth") or (coin == "usdc") or (coin == "usdt") or (coin == "shib") or (coin == "pussy") or (
            coin == "matic") or (coin == "bnb") or (coin == "busd") or (coin == "cds") or (coin == "op") or (
                  coin == "avax")):
        old_bal = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
        old_bal = old_bal[5]
        if old_bal == "":
            old_bal = Decimal("0.0")
        else:
            old_bal = Decimal(old_bal)
    elif ((coin == "sol")):
        old_bal = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
        old_bal = old_bal[5]
        if old_bal == "":
            old_bal = Decimal("0.0")
        else:
            old_bal = Decimal(old_bal)
    elif ((coin == "fluffy")):
        old_bal = await sql_select(wallet_db["sol"], "sol", "key_name", uttcex_id)
        old_bal = old_bal[6]
        if old_bal == "":
            old_bal = Decimal("0.0")
        else:
            old_bal = Decimal(old_bal)
    new_bal = str(format(amount + old_bal, decidic[coin]))
    if coin == "fluffy":
        await sql_update(wallet_db["sol"], "sol", "fluffy_instant_balance", new_bal, "key_name", uttcex_id)
    else:
        await sql_update(wallet_db[coin], coin, "instant_balance", new_bal, "key_name", uttcex_id)
    return


async def swap_debit(tid, coin: str, amount: str):
    amount = Decimal(format(amount, decidic[coin]))
    if (await has_profile(tid) == True):  # Sanity check 1
        pass
    if (await has_wallet(tid, coin) == True):  # Sanity check 2
        pass
    uttcex_id = await udefs.udefs.get_uid(tid)
    old_bal = 0
    # BITCOINLIB
    if ((coin == "btc") or (coin == "ltc") or (coin == "doge")):
        old_bal = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
        old_bal = old_bal[7]
        if old_bal == "":
            old_bal = Decimal("0.0")
        else:
            old_bal = Decimal(old_bal)
    # WEB3
    elif ((coin == "eth") or (coin == "usdc") or (coin == "usdt") or (coin == "shib") or (coin == "pussy") or (
            coin == "matic") or (coin == "bnb") or (coin == "busd") or (coin == "cds") or (coin == "op") or (
                  coin == "avax")):
        old_bal = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
        old_bal = old_bal[5]
        if old_bal == "":
            old_bal = Decimal("0.0")
        else:
            old_bal = Decimal(old_bal)
    elif ((coin == "sol")):
        old_bal = await sql_select(wallet_db[coin], coin, "key_name", uttcex_id)
        old_bal = old_bal[5]
        if old_bal == "":
            old_bal = Decimal("0.0")
        else:
            old_bal = Decimal(old_bal)
    elif ((coin == "fluffy")):
        old_bal = await sql_select(wallet_db["sol"], "sol", "key_name", uttcex_id)
        old_bal = old_bal[6]
        if old_bal == "":
            old_bal = Decimal("0.0")
        else:
            old_bal = Decimal(old_bal)
    new_bal = str(format(old_bal - amount, decidic[coin]))
    if coin == "fluffy":
        await sql_update(wallet_db["sol"], "sol", "fluffy_instant_balance", new_bal, "key_name", uttcex_id)
    else:
        await sql_update(wallet_db[coin], coin, "instant_balance", new_bal, "key_name", uttcex_id)
    return


async def dformat(s, f) -> Decimal:
    return Decimal(format(s, f))


async def true_uttcex_bal(coin: str) -> Decimal:
    bal = Decimal("0.0")
    staked = Decimal("0.0")
    if ((coin == "btc") or (coin == "ltc") or (coin == "doge")):
        bal = None
        try:
            bal = Decimal((await sql_select(wallet_db["sol"], "sol", "key_name", await udefs.udefs.get_uid(bot_ids[BOT_CFG_FLAG]["uttcex"])))[7])
        except:
            bal = Decimal("0.0")
        data = await sql_select("uttcex_bot_db", "locked_balance", "*", "*")
        if data is None:
            staked = Decimal("0.0")
        else:
            for stake in data:
                if stake[1] == coin and stake[0].startswith("stake") == True:
                    staked += Decimal(stake[2])
    elif ((coin == "eth") or (coin == "usdc") or (coin == "usdt") or (coin == "shib") or (coin == "pussy") or (
            coin == "matic") or (coin == "bnb") or (coin == "busd") or (coin == "cds") or (coin == "op") or (
                  coin == "avax")):
        bal = None
        try:
            bal = Decimal((await sql_select(wallet_db["sol"], "sol", "key_name", await udefs.udefs.get_uid(bot_ids[BOT_CFG_FLAG]["uttcex"])))[5])
        except:
            bal = Decimal("0.0")
        data = await sql_select("uttcex_bot_db", "locked_balance", "*", "*")
        if data is None:
            staked = Decimal("0.0")
        else:
            for stake in data:
                if stake[1] == coin and stake[0].startswith("stake") == True:
                    staked += Decimal(stake[2])
    elif ((coin == "xrp")):
        bal = None
        try:
            bal = Decimal((await sql_select(wallet_db["sol"], "sol", "key_name", await udefs.udefs.get_uid(bot_ids[BOT_CFG_FLAG]["uttcex"])))[5])
        except:
            bal = Decimal("0.0")
        data = await sql_select("uttcex_bot_db", "locked_balance", "*", "*")
        if data is None:
            staked = Decimal("0.0")
        else:
            for stake in data:
                if stake[1] == coin and stake[0].startswith("stake") == True:
                    staked += Decimal(stake[2])
    elif ((coin == "sol")):
        bal = None
        try:
            bal = Decimal((await sql_select(wallet_db["sol"], "sol", "key_name", await udefs.udefs.get_uid(bot_ids[BOT_CFG_FLAG]["uttcex"])))[5])
        except:
            bal = Decimal("0.0")
        data = await sql_select("uttcex_bot_db", "locked_balance", "*", "*")
        if data is None:
            staked = Decimal("0.0")
        else:
            for stake in data:
                if stake[1] == coin and stake[0].startswith("stake") == True:
                    staked += Decimal(stake[2])
    elif ((coin == "fluffy")):
        bal = None
        try:
            bal = Decimal((await sql_select(wallet_db["sol"], "sol", "key_name", await udefs.udefs.get_uid(bot_ids[BOT_CFG_FLAG]["uttcex"])))[6])
        except:
            bal = Decimal("0.0")
        data = await sql_select("uttcex_bot_db", "locked_balance", "*", "*")
        if data is None:
            staked = Decimal("0.0")
        else:
            for stake in data:
                if stake[1] == coin and stake[0].startswith("stake") == True:
                    staked += Decimal(stake[2])
    return Decimal(bal - staked)


async def swap(msg: discord.Message):
    global exenabled
    global waenabled
    main_profit_channel = 981665831861780521
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    epc = 3
    match (len(p)):
        case (4):
            if exenabled == False:
                await err(12, [msg])
                return
            amount = p[1]
            incoin = p[2]
            tmp = incoin
            outcoin = p[3]
            try:
                incoin = alias[incoin]
            except:
                await err(17, [msg])
                return
            try:
                outcoin = alias[outcoin]
            except:
                await err(17, [msg])
                return
            if incoin == outcoin:
                await err(-1, [msg, "Same-coin recursive swaps not enabled.\nSpecial secret feature in development."])
                return
            inprice = Decimal(format(await get_price(incoin), '.8f'))
            outprice = Decimal(format(await get_price(outcoin), '.8f'))
            inrate = rate_dic[incoin]
            rate = rate_dic[outcoin]
            uttcex_id = await udefs.udefs.get_uid(msg.author.id)
            discount = Decimal((await sql_select("uttcex_bot_db", "profiles", "uttcex_id", uttcex_id))[15])
            if (discount != Decimal(0.0)):
                discount = Decimal(format(discount / 100, '.2f'))
            palette = 0x4e8cd8
            if inrate == rate:
                rate = Decimal("0.98")
            elif inrate < rate:
                rate = inrate
                palette = coincolor[incoin]
            if (amount.find("$") == -1):  # Dollar sign not found
                amount = Decimal(amount)
                if (amount == Decimal("0.0")):
                    await err(8, [msg])
                    return
                if (tmp in atomnames):
                    amount = Decimal(format(await from_atomic(incoin, amount), decidic[incoin]))
                invalue = Decimal(format(inprice * amount, '.6f'))
                outvalue = Decimal(format(invalue * rate, '.6f'))
                fee = invalue - outvalue
                feeamount = Decimal(format(fee / outprice, decidic[outcoin]))
                outamount = Decimal(format((outvalue / outprice) - feeamount, decidic[outcoin]))
                feepct = int((1 - rate) * 100)
                e = discord.Embed(title="Swap your cryptocurrencies instantly!",
                                  description="Coins of equal rating will have a default 2% fee.\n\n", color=palette)
                e.set_author(name="Under The Table Centralized Exchange",
                             icon_url="https://media.discordapp.net/attachments/849759474868158504/1242229345846690012/image.png")
                e.add_field(name="Input Coin:",
                            value=f"{emojis[incoin]} __`{format(amount, decidic[incoin])}`__\nRate: **({inrate})**",
                            inline=True)
                e.add_field(name="Output Coin:",
                            value=f"{emojis[outcoin]} __`{format(outamount, decidic[outcoin])}`__\nRate: **({rate_dic[outcoin]})**",
                            inline=True)
                e.add_field(name="Fee Incurred:",
                            value=f"{emojis[outcoin]} __`{format(feeamount, decidic[outcoin])}`__\n**({emojis[outcoin]} ${fee})**\n**({feepct}%) ({rate})**",
                            inline=True)
                e.add_field(name="Input Value:", value=f"{emojis[incoin]} ${invalue}", inline=True)
                e.add_field(name="Output Value:", value=f"{emojis[outcoin]} ${outvalue}", inline=True)
                e.add_field(name="Discount:", value=f"**{int(discount * 100)}%**", inline=True)
                if (outamount < atomdic[outcoin]):
                    e.add_field(name="Notice:",
                                value=f"The output coin is too small.\n(`< {format(atomdic[outcoin], decidic[outcoin])}`)\nThis trade failed.",
                                inline=True)
                    e.color = 0xff0000
                    e.set_footer(
                        text="Prices powered by CoinGecko. UTTCex powered by Father Crypto and the UTTCex development team.")
                    await ereply(msg, e)
                    return
                elif (feeamount < atomdic[outcoin]):
                    e.add_field(name="Notice:",
                                value=f"No fee could be collected.\n(`< {format(atomdic[outcoin], decidic[outcoin])}`)\nThis trade failed.",
                                inline=True)
                    e.color = 0xff0000
                    e.set_footer(
                        text="Prices powered by CoinGecko. UTTCex powered by Father Crypto and the UTTCex development team.")
                    await ereply(msg, e)
                    return
            elif (amount.find("$") != -1):  # Dollar sign found
                value = Decimal(format(Decimal(await get_price(incoin)), decidic[incoin]))
                amount = Decimal(amount.replace("$", ""))
                zero = Decimal("0.0")
                amount = Decimal(format(amount / value, decidic[incoin]))
                if (amount <= (await dformat(zero, decidic[incoin]))):
                    await err(8, [msg])
                    return
                if (tmp in atomnames):
                    amount = Decimal(format(await from_atomic(incoin, amount), decidic[incoin]))
                invalue = Decimal(format(inprice * amount, '.6f'))
                outvalue = Decimal(format(invalue * rate, '.6f'))
                fee = invalue - outvalue
                feeamount = Decimal(format(fee / outprice, decidic[outcoin]))
                outamount = Decimal(format((outvalue / outprice) - feeamount, decidic[outcoin]))
                feepct = int((1 - rate) * 100)
                e = discord.Embed(title="Swap your cryptocurrencies instantly!",
                                  description="Coins of equal rating will have a default 2% fee.\n\n", color=palette)
                e.set_author(name="Under The Table Centralized Exchange",
                             icon_url="https://media.discordapp.net/attachments/849759474868158504/1242229345846690012/image.png")
                e.add_field(name="Input Coin:",
                            value=f"{emojis[incoin]} __`{format(amount, decidic[incoin])}`__\nRate: **({inrate})**",
                            inline=True)
                e.add_field(name="Output Coin:",
                            value=f"{emojis[outcoin]} __`{format(outamount, decidic[outcoin])}`__\nRate: **({rate_dic[outcoin]})**",
                            inline=True)
                e.add_field(name="Fee Incurred:",
                            value=f"{emojis[outcoin]} __`{format(feeamount, decidic[outcoin])}`__\n**({emojis[outcoin]} ${fee})**\n**({feepct}%) ({rate})**",
                            inline=True)
                e.add_field(name="Input Value:", value=f"{emojis[incoin]} ${invalue}", inline=True)
                e.add_field(name="Output Value:", value=f"{emojis[outcoin]} ${outvalue}", inline=True)
                e.add_field(name="Discount:", value=f"**{int(discount * 100)}%**", inline=True)
                if (outamount < atomdic[outcoin]):
                    e.description += "❌ **Swap failed.**"
                    e.add_field(name="Notice:",
                                value=f"The output coin is too small.\n(`< {format(atomdic[outcoin], decidic[outcoin])}`)\nThis trade failed.",
                                inline=True)
                    e.color = 0xff0000
                    e.set_footer(
                        text="Prices powered by CoinGecko. UTTCex powered by Father Crypto and the UTTCex development team.")
                    await ereply(msg, e)
                    return
                elif (feeamount < atomdic[outcoin]):
                    e.description += "❌ **Swap failed.**"
                    e.add_field(name="Notice:",
                                value=f"No fee could be collected.\n(`< {format(atomdic[outcoin], decidic[outcoin])}`)\nThis trade failed.",
                                inline=True)
                    e.color = 0xff0000
                    e.set_footer(
                        text="Prices powered by CoinGecko. UTTCex powered by Father Crypto and the UTTCex development team.")
                    await ereply(msg, e)
                    return
            b1 = await get_tip_bals(msg.author.id, bot_ids[BOT_CFG_FLAG]["uttcex"], incoin)
            sbal = await dformat(Decimal(b1[0]), decidic[incoin])
            ubal = await true_uttcex_bal(outcoin)
            if sbal < amount:
                await err(-1, [msg, "You cannot afford this swap."])
                return
            if ubal < outamount:
                await err(-1, [msg, "UTTCex cannot afford this swap."])
                return
            e.description += "✅ **Swap successful.**"
            # Debit the deposit
            # Credit the outamount
            await swap_debit(msg.author.id, incoin, amount)  # Take user coins
            await swap_credit(bot_ids[BOT_CFG_FLAG]["uttcex"], incoin, amount)  # Give to UTTCex
            await swap_debit(bot_ids[BOT_CFG_FLAG]["uttcex"], outcoin, outamount)  # Take UTTCex coins
            await swap_credit(msg.author.id, outcoin, outamount)  # Give to user
            waenabled = True
            e.set_footer(
                text="Prices powered by CoinGecko. UTTCex powered by Father Crypto and the UTTCex development team.")
            await ereply(msg, e)
            # Profit recording
            #
            # 50% to origin server
            # >> 50% goes to the server owner
            # >> 30% goes to staff
            # >> >> 50% goes to mods / admins
            # >> 10% goes to community airdrop rebate
            # >> 10% goes to whoever referred you (their referral code (uttcex ID))
            #
            # 25% goes to respective staking pool
            #
            # 10% goes to respective faucet
            #
            # 15% goes to UTTCex
            # >> 25% to Father Crypto
            # >> 25% to the Exchange Balance
            # >> 50% to staff
            # >> >> 50% to mods/admins
            # >> >> 50% to developers
            server_profit = format(feeamount / 2, '.20f')  # 50% to server

            server_owner_profit = format(Decimal(server_profit) / 2, '.20f')  # 50% to server owner
            owner = (await sql_select("uttcex_bot_db", "servers", "server_id", str(msg.guild.id)))[1]
            server_staff_profit = format(Decimal(server_profit) * Decimal("0.3"), '.20f')  # 30% to server staff

            server_mod_profit = format(Decimal(server_staff_profit) / 2, '.20f')  # Mod pay (50%)
            server_admin_profit = format(Decimal(server_staff_profit) / 2, '.20f')  # Admin pay (50%)

            community_profit = format(Decimal(server_profit) / 10, '.20f')  # Community Rebate
            referrer_profit = format(Decimal(server_profit) / 10, '.20f')  # Referrer's profit

            stake_pool_profit = format(feeamount * Decimal("0.3"), '.20f')  # Stake pool rewards
            await hardlock_bal(f"stake_profit_{msg.guild.id}", outcoin, stake_pool_profit)

            faucet_profit = format(feeamount * Decimal("0.1"), '.20f')  # Faucet reserve

            uttcex_profit = format(feeamount * Decimal("0.1"), '.20f')  # UTTCex Earnings
            fc_profit = format(Decimal(uttcex_profit) / 2, '.20f')  # Father Crypto profit
            ustaff_profit = format(Decimal(uttcex_profit) / 2, '.20f')  # UTTCex staff profit
            umodmin_profit = format(Decimal(ustaff_profit) / 2, '.20f')  # Mod/Admin profit
            dev_profit = format(Decimal(ustaff_profit) / 2, '.20f')  # Developer profit
            if (msg.guild.id != 824259447412359168):  # Not UTTCex main server, send their profit info
                data = await sql_select("uttcex_bot_db", "servers", "server_id", str(msg.guild.id))
                if data is None:
                    pass
                else:
                    e = discord.Embed(title="Swap fee collected.",
                                      description=f"Origin server: `{msg.guild.name}`\nServer ID: `{msg.guild.id}`\nUser: `{msg.author}`\nUser ID: `{msg.author.id}`",
                                      color=0x00ff00)
                    e.set_author(name="Under The Table Centralized Exchange",
                                 icon_url="https://media.discordapp.net/attachments/849759474868158504/1242229345846690012/image.png")
                    e.add_field(name="Input Coin:",
                                value=f"{emojis[incoin]} __`{format(amount, decidic[incoin])}`__\nRate: **({inrate})**",
                                inline=True)
                    e.add_field(name="Output Coin:",
                                value=f"{emojis[outcoin]} __`{format(outamount, decidic[outcoin])}`__\nRate: **({rate_dic[outcoin]})**",
                                inline=True)
                    e.add_field(name="Fee Incurred:",
                                value=f"{emojis[outcoin]} __`{format(feeamount, decidic[outcoin])}`__\n**({emojis[outcoin]} ${fee})**\n**({feepct}%) ({rate})**",
                                inline=True)
                    e.add_field(name="Server Reserved", value=f"{emojis[outcoin]} {server_profit}", inline=True)
                    e.add_field(name="Owner Profit", value=f"{emojis[outcoin]} {server_owner_profit}", inline=True)
                    e.add_field(name="Staff Profit", value=f"{emojis[outcoin]} {server_staff_profit}", inline=True)
                    e.add_field(name="Staff (Mod) Profit", value=f"{emojis[outcoin]} {server_mod_profit}", inline=True)
                    e.add_field(name="Staff (Admin) Profit", value=f"{emojis[outcoin]} {server_admin_profit}",
                                inline=True)
                    ch = client.get_channel(int(data[3]))
                    await ch.send(embed=e)
            e = discord.Embed(title="Swap fee collected.",
                              description=f"Origin server: `{msg.guild.name}`\nServer ID: `{msg.guild.id}`\nUser: `{msg.author}`\nUser ID: `{msg.author.id}`",
                              color=0x00ff00)
            e.set_author(name="Under The Table Centralized Exchange",
                         icon_url="https://media.discordapp.net/attachments/849759474868158504/1242229345846690012/image.png")
            e.add_field(name="Input Coin:",
                        value=f"{emojis[incoin]} __`{format(amount, decidic[incoin])}`__\nRate: **({inrate})**",
                        inline=True)
            e.add_field(name="Output Coin:",
                        value=f"{emojis[outcoin]} __`{format(outamount, decidic[outcoin])}`__\nRate: **({rate_dic[outcoin]})**",
                        inline=True)
            e.add_field(name="Fee Incurred:",
                        value=f"{emojis[outcoin]} __`{format(feeamount, decidic[outcoin])}`__\n**({emojis[outcoin]} ${fee})**\n**({feepct}%) ({rate})**",
                        inline=True)
            e.add_field(name="Server Reserved", value=f"{emojis[outcoin]} {server_profit}", inline=True)
            e.add_field(name="Owner Profit", value=f"{emojis[outcoin]} {server_owner_profit}", inline=True)
            e.add_field(name="Staff Profit", value=f"{emojis[outcoin]} {server_staff_profit}", inline=True)
            e.add_field(name="Staff (Mod) Profit", value=f"{emojis[outcoin]} {server_mod_profit}", inline=True)
            e.add_field(name="Staff (Admin) Profit", value=f"{emojis[outcoin]} {server_admin_profit}", inline=True)
            e.add_field(name="Stake Pool", value=f"{emojis[outcoin]} {stake_pool_profit}", inline=True)
            e.add_field(name="Faucet", value=f"{emojis[outcoin]} {faucet_profit}", inline=True)
            e.add_field(name="UTTCex Profit Reserved", value=f"{emojis[outcoin]} {uttcex_profit}", inline=True)
            e.add_field(name="Father Crypto", value=f"{emojis[outcoin]} {fc_profit}", inline=True)
            e.add_field(name="UTTCex Staff Reserved", value=f"{emojis[outcoin]} {ustaff_profit}", inline=True)
            e.add_field(name="UTTCex Mods/Admins", value=f"{emojis[outcoin]} {umodmin_profit}", inline=True)
            e.add_field(name="UTTCex Devs", value=f"{emojis[outcoin]} {dev_profit}", inline=True)
            ch = client.get_channel(main_profit_channel)
            await ch.send(embed=e)
            return
        case _:
            await err(2, [msg,
                          msg.content + "`\n\nExpected format:\n`u.swap` `{amount}` `coin 1` `coin 2`\n\nYou may use dollar ($) amounts as well",
                          epc, pg])
            return


# Advanced Commands #
async def netlink(msg: discord.Message):
    epc = 2
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    server = str(msg.guild.id)
    match (len(p)):
        case 1:
            e = Embed(title = "UTTCex.net Account Link",
                      description = "First, [create an account](https://uttcex.net/register.php) at **uttcex.net** if you do not have one.\n\nNext, use:\n\n`u.netlink prepare {your uttcex.net username here}`\n\nto prepare your account to be linked.\n\nFinally, enter your Discord ID at your [account settings](https://uttcex.net/account_settings.php) page.\n\n**Note:** You must be logged in to view your account settings page.",
                      color = 0xffffff)
            await msg.reply(embed = e)
            return
        case 3:
            # Link accounts
            if p[1].lower() == "prepare":
                username = p[2]
                data = await sql_select("uttcex_bot_db", "netlink", "discord_id", str(msg.author.id))
                if data is None:
                    data = await sql_insert("uttcex_bot_db", "netlink", "discord_id", str(msg.author.id))
                    await sql_update("uttcex_bot_db", "netlink", "username", username, "discord_id", str(msg.author.id))
                    await msg.reply("Your account is waiting to link.\n\nEnter your Discord ID in your [account settings](https://uttcex.net/account_settings.php) page.")
                    return
                else:
                    if data[2] == "1":
                        await msg.reply("Your account is already linked.")
                        return
                    await err(-1, [msg, f"Your account is already waiting to link\n\nEnter your Discord ID in your [account settings](https://uttcex.net/account_settings.php) page."])
                    return
                return
            else:
                await err(-1, [msg, f"Invalid parameter {p[1]}.\n\nUse `prepare` instead."])
                return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def whitelistcmd(msg: discord.Message):
    epc = 1
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    server = str(msg.guild.id)
    match (len(p)):
        case 1:
            e = Embed(title = "UTTCex.net Server Whitelist",
                      description = "**Usage:**\n> `u.whitelist request`\n\nSubmits a whitelist request for your server.",
                      color = 0xffffff)
            await msg.reply(embed = e)
            return
        case 2:
            match p[1].lower():
                case "request": # Request new
                    data = await sql_select("uttcex_bot_db", "whitelist_requests", "server_id", str(msg.guild.id))
                    if data is None:
                        await sql_insert("uttcex_bot_db", "whitelist_requests", "server_id", str(msg.guild.id))
                        e = Embed(title = "Whitelist Request",
                                  description = "Your request was submitted and is pending review.",
                                  color = 0xffffff)
                        await msg.reply(embed = e)
                        return
                    else:
                        if data[1] == "0":
                            e = Embed(title = "Whitelist Request",
                                      description = "Your request was submitted and is pending review.",
                                      color = 0xffffff)
                            await msg.reply(embed = e)
                            return
                        elif data[1] == "1":
                            e = Embed(title = "Whitelist Request",
                                      description = "Your request has been reviewed and is pending approval.",
                                      color = 0xffffff)
                            await msg.reply(embed = e)
                            return
                case _: # Invalid param
                    await err(-1, [msg, "Invalid option.\n\nValid options are: `request`"])
                    return
        case 3:
            match p[1].lower():
                case "review": # Admin must remove
                    match (msg.author.id in admin_list):
                        case (True):
                            server = p[2]
                            try:
                                await sql_update("uttcex_bot_db", "whitelist_requests", "reviewed", "1", "server_id", server)
                            except:
                                await msg.reply(f"Failed to update reviewed status server ID: {server}")
                                return
                            await msg.reply(f"Reviewed server ID: {server}")
                            return
                        case (False):
                            await err(1, [msg])
                            return
                case "approve": # Admin must approve
                    match (msg.author.id in admin_list):
                        case (True):
                            server = p[2]
                            try:
                                await sql_delete("uttcex_bot_db", "whitelist_requests", "server_id", server)
                            except:
                                return
                            data = await sql_select("uttcex_bot_db", "whitelist", "server_id", server)
                            if data is None:
                                await sql_insert("uttcex_bot_db", "whitelist", "server_id", server)
                                await sql_update("uttcex_bot_db", "whitelist", "bot_cfg_flag", str(BOT_CFG_FLAG), "server_id", server)
                                await msg.reply(f"Approved server ID: {server}")
                                return
                            else:
                                e = Embed(title = "Whitelist Status",
                                          description = "Already added to the whitelist.",
                                          color = 0xffffff)
                                await msg.reply(embed = e)
                                return
                        case (False):
                            await err(1, [msg])
                            return
                case "deny": # Admin must deny
                    match (msg.author.id in admin_list):
                        case (True):
                            server = p[2]
                            await msg.reply(f"Denied server ID: {server}")
                            try:
                                await sql_delete("uttcex_bot_db", "whitelist_requests", "server_id", server)
                            except:
                                return
                            return
                        case (False):
                            await err(1, [msg])
                            return
                case "remove": # Admin must remove
                    match (msg.author.id in admin_list):
                        case (True):
                            server = p[2]
                            await msg.reply(f"Removed server ID: {server}")
                            try:
                                await sql_delete("uttcex_bot_db", "whitelist_requests", "server_id", server)
                            except:
                                pass
                            try:
                                await sql_delete("uttcex_bot_db", "whitelist", "server_id", server)
                            except:
                                return
                        case (False):
                            await err(1, [msg])
                            return
                case "status": # Admin must remove
                    match (msg.author.id in admin_list):
                        case (True):
                            server = p[2]
                            data = await sql_select("uttcex_bot_db", "whitelist", "server_id", server)
                            if data is not None:
                                e = Embed(title = "Whitelist Status",
                                          description = "Approved and added to the whitelist.",
                                          color = 0xffffff)
                                await msg.reply(embed = e)
                                return
                            else:
                                data = await sql_select("uttcex_bot_db", "whitelist_requests", "server_id", server)
                                if data is None:
                                    e = Embed(title = "Whitelist Status",
                                              description = "Server has not requested whitelist yet.",
                                              color = 0xffffff)
                                    await msg.reply(embed = e)
                                    return
                                else:
                                    if data[1] == "0":
                                        e = Embed(title = "Whitelist Request",
                                                  description = "Whitelist was submitted and is pending review.",
                                                  color = 0xffffff)
                                        await msg.reply(embed = e)
                                        return
                                    elif data[1] == "1":
                                        e = Embed(title = "Whitelist Request",
                                                  description = "Whitelist has been reviewed and is pending approval.",
                                                  color = 0xffffff)
                                        await msg.reply(embed = e)
                                        return
                        case (False):
                            await err(1, [msg])
                            return
                case _:
                    await err(2, [msg, msg.content, epc, pg])
                    return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


# Host Commands #
async def config(msg: Message):
    tmp = msg.content.lower()
    t = list(tmp.split(" "))
    match len(t):
        case 4: # Setting a flag to a value
            t[3] = await udefs.udefs.stripid(t[3])
            match t[1]:
                case "set":
                    match t[2]:
                        case "owner":
                            await usql.usql.sql_update("uttcex_bot_db", "servers", "owner_id", t[3], "server_id", str(msg.guild.id))
                            e = Embed(title = "Configuration updated.",
                                      description = f"Server owner set to:\n> <@{t[3]}>",
                                      color = 0x00ff00)
                            await msg.reply(embed = e)
                            return
                        case "lc":
                            await usql.usql.sql_update("uttcex_bot_db", "servers", "log_channel_id", t[3], "server_id", str(msg.guild.id))
                            e = Embed(title = "Configuration updated.",
                                      description = f"Server log channel set to:\n> <#{t[3]}>",
                                      color = 0x00ff00)
                            await msg.reply(embed = e)
                            return
                        case "ul":
                            await usql.usql.sql_update("uttcex_bot_db", "servers", "uttcex_log_channel", t[3], "server_id", str(msg.guild.id))
                            e = Embed(title = "Configuration updated.",
                                      description = f"UTTCex global log and updates channel set to:\n> <#{t[3]}>",
                                      color = 0x00ff00)
                            await msg.reply(embed = e)
                            return
                        case "tc":
                            await usql.usql.sql_update("uttcex_bot_db", "servers", "trade_channel_id", t[3], "server_id", str(msg.guild.id))
                            e = Embed(title = "Configuration updated.",
                                      description = f"Trade channel set to:\n> <#{t[3]}>",
                                      color = 0x00ff00)
                            await msg.reply(embed = e)
                            return
                        case "ac":
                            await usql.usql.sql_update("uttcex_bot_db", "servers", "airdrop_channel_id", t[3], "server_id", str(msg.guild.id))
                            e = Embed(title = "Configuration updated.",
                                      description = f"Airdrop channel set to:\n> <#{t[3]}>",
                                      color = 0x00ff00)
                            await msg.reply(embed = e)
                            return
                        case "tlc":
                            await usql.usql.sql_update("uttcex_bot_db", "servers", "tip_log_channel", t[3], "server_id", str(msg.guild.id))
                            e = Embed(title = "Configuration updated.",
                                      description = f"Tip log channel set to:\n> <#{t[3]}>",
                                      color = 0x00ff00)
                            await msg.reply(embed = e)
                            return
                        case "plc":
                            await usql.usql.sql_update("uttcex_bot_db", "servers", "profit_log_channel", t[3], "server_id", str(msg.guild.id))
                            e = Embed(title = "Configuration updated.",
                                      description = f"Profit log channel set to:\n> <#{t[3]}>",
                                      color = 0x00ff00)
                            await msg.reply(embed = e)
                            return
                        case _:
                            e = Embed(title = "Error",
                                      description = f"Invalid configuration flag `{t[2]}`",
                                      color = 0xff0000)
                            await msg.reply(embed = e)
                            return
        case 2:
            match t[1]:
                case "reset":
                    await usql.usql.sql_update("uttcex_bot_db", "servers", "log_channel_id", "0", "server_id", str(msg.guild.id))
                    await usql.usql.sql_update("uttcex_bot_db", "servers", "uttcex_log_channel", "0", "server_id", str(msg.guild.id))
                    await usql.usql.sql_update("uttcex_bot_db", "servers", "trade_channel_id", "0", "server_id", str(msg.guild.id))
                    await usql.usql.sql_update("uttcex_bot_db", "servers", "airdrop_channel_id", "0", "server_id", str(msg.guild.id))
                    await usql.usql.sql_update("uttcex_bot_db", "servers", "tip_log_channel", "0", "server_id", str(msg.guild.id))
                    await usql.usql.sql_update("uttcex_bot_db", "servers", "profit_log_channel", "0", "server_id", str(msg.guild.id))
                    e = Embed(title = "Configuration updated.",
                              description = f"All configuration flags reset.",
                              color = 0x0000ff)
                    await msg.reply(embed = e)
                    return
            return
        case 3:
            e = Embed(title = "Error",
                      description = "Invalid number of flags provided. Missing `1`",
                      color = 0xff0000)
            await msg.reply(embed = e)
            return
        case _: # Show config status for server
            if (await has_server(msg.guild.id)) is True:
                pass # Sanity check
            cfgs = await usql.usql.sql_select("uttcex_bot_db", "servers", "server_id", str(msg.guild.id))
            e = Embed(title = "Server Configuration:",
                      description = await udefs.udefs.config_string(cfgs),
                      color = 0xffffff)
            await msg.reply(embed = e)
            return


async def stafflist(msg: discord.Message):
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    server = str(msg.guild.id)
    match (len(p)):
        case (1):
            data = await sql_select("uttcex_bot_db", "server_staff_list", "*", "*")
            staff = []
            stafflist = ""
            for x in data:
                if x[0] == server:
                    staff.append([x[1], x[2]])
            for user in staff:
                stype = ""
                if (user[1] == "5"):
                    stype = "UTTCex Moderator"
                elif (user[1] == "6"):
                    stype = "UTTCex Administrator"
                elif (user[1] == "7"):
                    stype = "UTTCex Developer"
                elif (user[1] == "10"):
                    stype = "UTTCex Super Admin"
                if (user[1] == "3"):
                    stype = "Server Owner"
                elif (user[1] == "2"):
                    stype = "Server Administrator"
                elif (user[1] == "1"):
                    stype = "Server Moderator"
                stafflist += f"<@{user[0]}> | **{stype}**\n"
            e = discord.Embed(title="This Server's Staff", description=stafflist, color=0xffffff)
            await ereply(msg, e)
            return
        case _:
            await err(2, [msg, msg.content, "Variable", pg])
            return


async def purge(msg: discord.Message):
    await msg.delete()
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    epc = 1
    pg = len(p) -1
    match (len(p)):
        case (2):
            limit = int(p[1])
            await msg.channel.purge(limit=limit)
            await msg.channel.send(f"Purged {limit} messages.", delete_after=5)
        case _:
            return


    # Admins #
async def say(msg):
    await msg.reply(msg.content[6:])
    return

async def is_staff(server, target) -> bool:
    data = await sql_select("uttcex_bot_db", "server_staff_list", "*", "*")
    flag = False
    if data is not None:
        for x in data:
            if x[0] == server and x[1] == target:
                flag = True
    return flag

async def is_server_owner(server, target) -> bool:
    data = await sql_select("uttcex_bot_db", "servers", "*", "*")
    for x in data:
        if ((x[0] == server) and (x[1] == target)):
            return True
    return False

async def remove_staff(msg: discord.Message):
    epc = 1
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (2):
            auth = str(await get_auth(msg.author.id))
            target = await stripid(p[1])
            server = str(msg.guild.id)
            if ((await has_profile(target)) == True):
                pass
            if auth == "3":
                b = await is_server_owner(server,target)
                if b is True:
                    await sql_do("uttcex_bot_db", f"DELETE FROM `server_staff_list` WHERE `staff_id`=\"{target}\" AND `server_id`=\"{server}\"")
                    e = discord.Embed(title = "Staff Removed", description = f"<@{target}> was removed from staff.")
                    await msg.reply(embed = e)
                    return
                else:
                    e = discord.Embed(title = "Unauthorized.", description = "You may only perform this action in your server.", color = 0xff0000)
                    await msg.reply(embed = e)
                    return
            elif auth == "10":
                await sql_do("uttcex_bot_db", f"DELETE FROM `server_staff_list` WHERE `staff_id`=\"{target}\" AND `server_id`=\"{server}\"")
                e = discord.Embed(title = "Staff Removed", description = f"<@{target}> was removed from staff.")
                await msg.reply(embed = e)
                return
        case _:
            await err(2, [msg, msg.content + "\n{ID}", epc, pg])
            return
    return

async def set_staff(msg: discord.Message):
    epc = 2
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (3):
            auth = str(await get_auth(msg.author.id))
            target = await stripid(p[1])
            server = str(msg.guild.id)
            if ((await has_profile(target)) == True):
                pass
            stype = (await sanistr(p[2])).lower()
            if auth == "3":
                if ((stype == "mod") or (stype == "moderator")):
                    b = await is_staff(server, target)
                    if b is False:
                        await sql_do("uttcex_bot_db", f"INSERT INTO `server_staff_list`(`server_id`,`staff_id`,`staff_auth`) VALUES (\"{server}\", \"{target}\", \"1\")")
                    elif b is True:
                        await sql_do("uttcex_bot_db", f"UPDATE `server_staff_list` SET `staff_auth`=\"1\" WHERE `server_id`=\"{server}\" AND `staff_id`=\"{target}\"")
                    e = discord.Embed(title="Staff Set",
                                      description=f"You have set <@{target}> as a moderator for this server.\n\nThey will earn a portion of the fees collected for staff.",
                                      color=0xaa00aa)
                    await ereply(msg, e)
                    return
                elif ((stype == "admin") or (stype == "administrator")):
                    b = await is_staff(server, target)
                    if b is False:
                        await sql_do("uttcex_bot_db", f"INSERT INTO `server_staff_list`(`server_id`,`staff_id`,`staff_auth`) VALUES (\"{server}\", \"{target}\", \"2\")")
                    elif b is True:
                        await sql_do("uttcex_bot_db", f"UPDATE `server_staff_list` SET `staff_auth`=\"2\" WHERE `server_id`=\"{server}\" AND `staff_id`=\"{target}\"")
                    e = discord.Embed(title="Staff Set",
                                      description=f"You have set <@{target}> as an administrator for this server.\n\nThey will earn a portion of the fees collected for staff.",
                                      color=0xaa00aa)
                    await ereply(msg, e)
                    return
                else:
                    await err(-1, [msg,
                                   "Invalid flag.\n\nValid flags are:\n```mod, moderator\nadmin, administrator\n```\nNot case-sensitive."])
                    return
            elif (auth == "9") or (auth == "10"):
                if (msg.guild.id == 1051896202192502844):
                    if ((stype == "mod") or (stype == "moderator")):
                        b = await is_staff(server, target)
                        if b is False:
                            await sql_do("uttcex_bot_db",
                                         f"INSERT INTO `server_staff_list`(`server_id`,`staff_id`,`staff_auth`) VALUES (\"{server}\", \"{target}\", \"4\")")
                        elif b is True:
                            await sql_do("uttcex_bot_db",
                                         f"UPDATE `server_staff_list` SET `staff_auth`=\"5\" WHERE `server_id`=\"{server}\" AND `staff_id`=\"{target}\"")
                        await sql_update("uttcex_bot_db", "profiles", "uttcex_staff", "1", "discord_id", target)
                        await sql_update("uttcex_bot_db", "profiles", "auth_level", "5", "discord_id", target)
                        e = discord.Embed(title="Staff Set",
                                          description=f"You have set <@{target}> as a moderator for this server.\n\nThey will earn a portion of the fees collected for staff.",
                                          color=0xaa00aa)
                        await ereply(msg, e)
                        return
                    if ((stype == "exop") or (stype == "exchangeoperator")):
                        b = await is_staff(server, target)
                        if b is False:
                            await sql_do("uttcex_bot_db",
                                         f"INSERT INTO `server_staff_list`(`server_id`,`staff_id`,`staff_auth`) VALUES (\"{server}\", \"{target}\", \"5\")")
                        elif b is True:
                            await sql_do("uttcex_bot_db",
                                         f"UPDATE `server_staff_list` SET `staff_auth`=\"5\" WHERE `server_id`=\"{server}\" AND `staff_id`=\"{target}\"")
                        await sql_update("uttcex_bot_db", "profiles", "uttcex_staff", "1", "discord_id", target)
                        await sql_update("uttcex_bot_db", "profiles", "auth_level", "5", "discord_id", target)
                        e = discord.Embed(title="Staff Set",
                                          description=f"You have set <@{target}> as an exchange operator for this server.",
                                          color=0xaa00aa)
                        await ereply(msg, e)
                        return
                    elif ((stype == "admin") or (stype == "administrator")):
                        b = await is_staff(server, target)
                        if b is False:
                            await sql_do("uttcex_bot_db",
                                         f"INSERT INTO `server_staff_list`(`server_id`,`staff_id`,`staff_auth`) VALUES (\"{server}\", \"{target}\", \"6\")")
                        elif b is True:
                            await sql_do("uttcex_bot_db",
                                         f"UPDATE `server_staff_list` SET `staff_auth`=\"6\" WHERE `server_id`=\"{server}\" AND `staff_id`=\"{target}\"")
                        await sql_update("uttcex_bot_db", "profiles", "uttcex_staff", "1", "discord_id", target)
                        await sql_update("uttcex_bot_db", "profiles", "auth_level", "6", "discord_id", target)
                        e = discord.Embed(title="Staff Set",
                                          description=f"You have set <@{target}> as an administrator for this server.\n\nThey will earn a portion of the fees collected for staff.",
                                          color=0xaa00aa)
                        await ereply(msg, e)
                        return
                    elif ((stype == "dev") or (stype == "developer")):
                        b = await is_staff(server, target)
                        if b is False:
                            await sql_do("uttcex_bot_db",
                                         f"INSERT INTO `server_staff_list`(`server_id`,`staff_id`,`staff_auth`) VALUES (\"{server}\", \"{target}\", \"7\")")
                        elif b is True:
                            await sql_do("uttcex_bot_db",
                                         f"UPDATE `server_staff_list` SET `staff_auth`=\"1\" WHERE `server_id`=\"{server}\" AND `staff_id`=\"{target}\"")
                        await sql_update("uttcex_bot_db", "profiles", "uttcex_staff", "7", "discord_id", target)
                        await sql_update("uttcex_bot_db", "profiles", "auth_level", "7", "discord_id", target)
                        e = discord.Embed(title="Staff Set",
                                          description=f"You have set <@{target}> as a developer for this server.\n\nThey will earn a portion of the fees collected for staff.",
                                          color=0xaa00aa)
                        await ereply(msg, e)
                        return
                    elif (stype == "superadmin"):
                        b = await is_staff(server, target)
                        if b is False:
                            await sql_do("uttcex_bot_db",
                                         f"INSERT INTO `server_staff_list`(`server_id`,`staff_id`,`staff_auth`) VALUES (\"{server}\", \"{target}\", \"9\")")
                        elif b is True:
                            await sql_do("uttcex_bot_db",
                                         f"UPDATE `server_staff_list` SET `staff_auth`=\"10\" WHERE `server_id`=\"{server}\" AND `staff_id`=\"{target}\"")
                        await sql_update("uttcex_bot_db", "profiles", "uttcex_staff", "1", "discord_id", target)
                        await sql_update("uttcex_bot_db", "profiles", "auth_level", "10", "discord_id", target)
                        e = discord.Embed(title="Staff Set",
                                          description=f"You have set <@{target}> as a super administrator for this server.\n\nThey will earn a portion of the fees collected for staff.",
                                          color=0xaa00aa)
                        await ereply(msg, e)
                        return
                    else:
                        await err(-1, [msg,
                                       "Invalid flag.\n\nValid flags are:\n```mod, moderator\nadmin, administrator\ndev, developer```\nNot case-sensitive."])
                        return
                else:  # Not UTTCex
                    if ((stype == "mod") or (stype == "moderator")):
                        b = await is_staff(server, target)
                        if b is False:
                            await sql_do("uttcex_bot_db",
                                         f"INSERT INTO `server_staff_list`(`server_id`,`staff_id`,`staff_auth`) VALUES (\"{server}\", \"{target}\", \"1\")")
                        elif b is True:
                            await sql_do("uttcex_bot_db",
                                         f"UPDATE `server_staff_list` SET `staff_auth`=\"1\" WHERE `server_id`=\"{server}\" AND `staff_id`=\"{target}\"")
                        e = discord.Embed(title="Staff Set",
                                          description=f"You have set <@{target}> as a moderator for this server.\n\nThey will earn a portion of the fees collected for staff.",
                                          color=0xaa00aa)
                        await ereply(msg, e)
                        return
                    elif ((stype == "admin") or (stype == "administrator")):
                        b = await is_staff(server, target)
                        if b is False:
                            await sql_do("uttcex_bot_db",
                                         f"INSERT INTO `server_staff_list`(`server_id`,`staff_id`,`staff_auth`) VALUES (\"{server}\", \"{target}\", \"2\")")
                        elif b is True:
                            await sql_do("uttcex_bot_db",
                                         f"UPDATE `server_staff_list` SET `staff_auth`=\"2\" WHERE `server_id`=\"{server}\" AND `staff_id`=\"{target}\"")
                        e = discord.Embed(title="Staff Set",
                                          description=f"You have set <@{target}> as an administrator for this server.\n\nThey will earn a portion of the fees collected for staff.",
                                          color=0xaa00aa)
                        await ereply(msg, e)
                        return
                    else:
                        await err(-1, [msg,
                                       "Invalid flag.\n\nValid flags are:\n```mod, moderator\nadmin, administrator\ndev, developer```\nNot case-sensitive."])
                        return
        case _:
            await err(2, [msg, msg.content + "\n{ID}", epc, pg])
            return


async def set_auth(msg: discord.Message):
    epc = 2
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (3):
            if (await has_profile(p[1]) == True):
                await sql_update("uttcex_bot_db", "profiles", "auth_level", p[2], "discord_id", await stripid(p[1]))
                await reply(msg, "AUTH SET")
                return
        case _:
            await err(2, [msg, msg.content + "\n{ID} {auth_level}", epc, pg])
            return

async def uttcex_ban(uid: str) -> None:
    discord_id = await udefs.udefs.get_discord_id_from_uid(uid)
    await sql_update("uttcex_bot_db", "profiles", "is_banned", "1", "discord_id", str(discord_id))
    return

async def uttcex_id_ban(tid: str) -> None:
    await sql_update("uttcex_bot_db", "profiles", "is_banned", "1", "discord_id", tid)
    return

async def u_ban(msg: discord.Message):
    epc = 1
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (2):
            if (await has_profile(p[1]) == True):
                auth1 = await get_auth(msg.author.id)
                auth2 = await get_auth(await stripid(p[1]))
                if auth1 < auth2:
                    await err(1, [msg, msg.content])
                    return
                if (int(p[1]) == int(msg.author.id)):
                    await err(-1, [msg, "You can't ban yourself!"])
                    return
                print(p[1])
                uid = await get_uid(await stripid(p[1]))
                await sql_update("uttcex_bot_db", "profiles", "is_banned", "1", "discord_id", await stripid(p[1]))
                #await uttcex_id_ban(uid)
                e = discord.Embed(title="Banned user from UTTCex.",
                                  description=f"ID: `{await stripid(p[1])}` has been banned from using UTTCex.",
                                  color=0xff0000)
                await ereply(msg, e)
                return
        case (3):
            if (await has_profile(p[1]) == True):
                uid = await get_uid(await stripid(p[1]))
                await sql_update("uttcex_bot_db", "profiles", "is_banned", "1", "discord_id", await stripid(p[1]))
                reason = " ".join(p[2:])
                await sql_update("uttcex_bot_db", "profiles", "ban_reason", reason, "discord_id", await stripid(p[1]))
                e = discord.Embed(title="Banned user from UTTCex.",
                                  description=f"ID: `{await stripid(p[1])}` has been banned from using UTTCex.\n\n**Reason:** `{reason}`.",
                                  color=0xff0000)
                await ereply(msg, e)
                return
        case _:
            match (p[2].lower()):
                case ("reason"):
                    if (await has_profile(p[1]) == True):
                        reason = " ".join(p[3:])
                        uid = await get_uid(await stripid(p[1]))
                        await sql_update("uttcex_bot_db", "profiles", "is_banned", "1", "discord_id", await stripid(p[1]))
                        await sql_update("uttcex_bot_db", "profiles", "ban_reason", reason, "discord_id",
                                         await stripid(p[1]))
                        e = discord.Embed(title="Set reason.",
                                          description=f"ID: `{await stripid(p[1])}`\n\n**Reason:** `{reason}`.",
                                          color=0xff0000)
                        await ereply(msg, e)
                        return
                case ("additional"):
                    if (await has_profile(p[1]) == True):
                        additional = " ".join(p[3:])
                        uid = await get_uid(await stripid(p[1]))
                        await sql_update("uttcex_bot_db", "profiles", "is_banned", "1", "discord_id", await stripid(p[1]))
                        await sql_update("uttcex_bot_db", "profiles", "additional_reason", additional, "discord_id",
                                         await stripid(p[1]))
                        e = discord.Embed(title="Set additional information.",
                                          description=f"ID: `{await stripid(p[1])}`\n\n**Reason:** `{additional}`.",
                                          color=0xff0000)
                        await ereply(msg, e)
                        return


async def u_unban(msg: discord.Message):
    epc = 1
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (2):
            if (await has_profile(p[1]) == True):
                await sql_update("uttcex_bot_db", "profiles", "is_banned", "0", "discord_id", await stripid(p[1]))
                e = discord.Embed(title="Unbanned user from UTTCex.",
                                  description=f"ID: `{await stripid(p[1])}` has been unbanned from using UTTCex.",
                                  color=0x00ff00)
                await ereply(msg, e)
                return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def u_enable(msg: discord.Message):
    global admin_only
    global active_discrepancy
    epc = 1
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (2):
            p[1] = p[1].lower()
            match (p[1]):
                case ("core"):
                    if (active_discrepancy == True):
                        await err(-1, [msg,
                                       "```ansi\n\u001b[0;40;31mNot even you are allowed to enable the core\nduring an active discrepancy.\n\nThis must be fixed before activation is permitted.\u001b[0;0m\n```"])
                        return
                    await sql_update("uttcex_bot_db", "uttcex_status", "swapping", "1", "row_id", "0")
                    await sql_update("uttcex_bot_db", "uttcex_status", "staking", "1", "row_id", "0")
                    await sql_update("uttcex_bot_db", "uttcex_status", "escrow", "1", "row_id", "0")
                    await sql_update("uttcex_bot_db", "uttcex_status", "loan", "1", "row_id", "0")
                    await sql_update("uttcex_bot_db", "uttcex_status", "instant_wallets", "1", "row_id", "0")
                    await sql_update("uttcex_bot_db", "uttcex_status", "feature_deposits", "1", "row_id", "0")
                    await reply(msg, "✅ **Core __enabled__.**")
                    await server_log_broadcast("", "", 1)
                    return
                case ("deposits"):
                    if (active_discrepancy == True):
                        await err(-1, [msg,
                                       "```ansi\n\u001b[0;40;31mNot even you are allowed to enable the core\nduring an active discrepancy.\n\nThis must be fixed before activation is permitted.\u001b[0;0m\n```"])
                        return
                    if (bool(int(data[5])) == False):
                        await err(-1, [msg, "Wallets must be enabled first."])
                        return
                    await sql_update("uttcex_bot_db", "uttcex_status", "feature_deposits", "1", "row_id", "0")
                    await reply(msg, "✅ **Feature Deposits __enabled__.**")
                    return
                case ("wallets"):
                    if (active_discrepancy == True):
                        await err(-1, [msg,
                                       "```ansi\n\u001b[0;40;31mNot even you are allowed to enable wallets\nduring an active discrepancy.\n\nThis must be fixed before activation is permitted.\u001b[0;0m\n```"])
                        return
                    await sql_update("uttcex_bot_db", "uttcex_status", "instant_wallets", "1", "row_id", "0")
                    await reply(msg, "✅ **Instant Wallets __enabled__.**")
                    return
                case ("swapping"):
                    if (active_discrepancy == True):
                        await err(-1, [msg,
                                       "```ansi\n\u001b[0;40;31mNot even you are allowed to enable wallets\nduring an active discrepancy.\n\nThis must be fixed before activation is permitted.\u001b[0;0m\n```"])
                        return
                    data = await sql_select("uttcex_bot_db", "uttcex_status", "row_id", "0")
                    if (bool(int(data[5])) == False):
                        await err(-1, [msg, "Wallets must be enabled first."])
                        return
                    await sql_update("uttcex_bot_db", "uttcex_status", "swapping", "1", "row_id", "0")
                    await reply(msg, "✅ **Exchange __enabled__.**")
                    return
                case ("staking"):
                    if (active_discrepancy == True):
                        await err(-1, [msg,
                                       "```ansi\n\u001b[0;40;31mNot even you are allowed to enable wallets\nduring an active discrepancy.\n\nThis must be fixed before activation is permitted.\u001b[0;0m\n```"])
                        return
                    data = await sql_select("uttcex_bot_db", "uttcex_status", "row_id", "0")
                    if (bool(int(data[5])) == False):
                        await err(-1, [msg, "Wallets must be enabled first."])
                        return
                    await sql_update("uttcex_bot_db", "uttcex_status", "swapping", "1", "row_id", "0")
                    await reply(msg, "✅ **Staking __enabled__.**")
                    return
                case ("loans"):
                    if (active_discrepancy == True):
                        await err(-1, [msg,
                                       "```ansi\n\u001b[0;40;31mNot even you are allowed to enable wallets\nduring an active discrepancy.\n\nThis must be fixed before activation is permitted.\u001b[0;0m\n```"])
                        return
                    data = await sql_select("uttcex_bot_db", "uttcex_status", "row_id", "0")
                    if (bool(int(data[5])) == False):
                        await err(-1, [msg, "Wallets must be enabled first."])
                        return
                    await sql_update("uttcex_bot_db", "uttcex_status", "loan", "1", "row_id", "0")
                    await reply(msg, "✅ **Loans __enabled__.**")
                    return
                case ("escrow"):
                    if (active_discrepancy == True):
                        await err(-1, [msg,
                                       "```ansi\n\u001b[0;40;31mNot even you are allowed to enable wallets\nduring an active discrepancy.\n\nThis must be fixed before activation is permitted.\u001b[0;0m\n```"])
                        return
                    if (bool(int(data[5])) == False):
                        await err(-1, [msg, "Wallets must be enabled first."])
                        return
                    await sql_update("uttcex_bot_db", "uttcex_status", "escrow", "1", "row_id", "0")
                    await reply(msg, "✅ **Escrow __enabled__.**")
                    return
                case ("admin-only"):
                    admin_only = True
                    await reply(msg, "✅ **Admin-Only __enabled__.** ✅")
                    return
                case _:
                    return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def u_disable(msg: discord.Message):
    global admin_only
    epc = 1
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (2):
            match (p[1]):
                case ("core"):
                    await sql_update("uttcex_bot_db", "uttcex_status", "swapping", "0", "row_id", "0")
                    await sql_update("uttcex_bot_db", "uttcex_status", "staking", "0", "row_id", "0")
                    await sql_update("uttcex_bot_db", "uttcex_status", "escrow", "0", "row_id", "0")
                    await sql_update("uttcex_bot_db", "uttcex_status", "loan", "0", "row_id", "0")
                    await sql_update("uttcex_bot_db", "uttcex_status", "instant_wallets", "0", "row_id", "0")
                    await sql_update("uttcex_bot_db", "uttcex_status", "feature_deposits", "0", "row_id", "0")
                    await reply(msg, "❌ **Core __disabled__.**")
                    await server_log_broadcast("", "", 1)
                    return
                case ("deposits"):
                    await sql_update("uttcex_bot_db", "uttcex_status", "feature_deposits", "0", "row_id", "0")
                    await reply(msg, "❌ **Feature Deposits __disabled__.**")
                    return
                case ("wallets"):
                    await sql_update("uttcex_bot_db", "uttcex_status", "instant_wallets", "0", "row_id", "0")
                    await reply(msg, "❌ **Instant Wallets __disabled__.**")
                    return
                case ("swapping"):
                    data = await sql_select("uttcex_bot_db", "uttcex_status", "row_id", "0")
                    await sql_update("uttcex_bot_db", "uttcex_status", "swapping", "0", "row_id", "0")
                    await reply(msg, "❌ **Exchange __disabled__.**")
                    return
                case ("staking"):
                    data = await sql_select("uttcex_bot_db", "uttcex_status", "row_id", "0")
                    await sql_update("uttcex_bot_db", "uttcex_status", "staking", "0", "row_id", "0")
                    await reply(msg, "❌ **Staking __disabled__.**")
                    return
                case ("loans"):
                    data = await sql_select("uttcex_bot_db", "uttcex_status", "row_id", "0")
                    await sql_update("uttcex_bot_db", "uttcex_status", "loan", "0", "row_id", "0")
                    await reply(msg, "❌ **Loans __disabled__.**")
                    return
                case ("escrow"):
                    await sql_update("uttcex_bot_db", "uttcex_status", "escrow", "0", "row_id", "0")
                    await reply(msg, "❌ **Escrow __disabled__.**")
                    return
                case ("admin-only"):
                    admin_only = False
                    await reply(msg, "❌ **Admin-Only __disabled__.** ❌")
                    return
                case _:
                    return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return

async def server_log_broadcast(title: str, description: str, flag: int):
    footer = str(await timestamp())
    match (flag):
        case (1): # Core Enabled
            for g in client.guilds:
                if (await has_server(g.id)) is True: # Sanity check, create server config if nonexistent
                    pass
                data = await sql_select("uttcex_bot_db", "servers", "server_id", str(g.id))
                ch = int(data[3])
                print(f"{g.name} - #{ch}")
                ch = client.get_channel(ch)
                e = Embed(title = "UTTCex Global Announcement Log Message",
                          description = "## UTTCex service has been re-enabled.\n\nYour server will now resume any activities that did not complete prior to the platform becoming disabled.",
                          color = 0x00ff00)
                e.set_footer(text=footer)
                try:
                    await ch.send(embed = e)
                except:
                    if g.id not in whitelist[BOT_CFG_FLAG]:
                        print(f"Server {g.name} not whitelisted. Passing.")
                        continue
            return
        case (-1): # Core Disabled
            for g in client.guilds:
                if (await has_server(g.id)) is True: # Sanity check, create server config if nonexistent
                    pass
                data = await sql_select("uttcex_bot_db", "servers", "server_id", str(g.id))
                ch = int(data[3])
                print(f"{g.name} - #{ch}")
                ch = client.get_channel(ch)
                e = Embed(title = "UTTCex Global Announcement Log Message",
                          description = "## UTTCex has been automatically disabled due to an internal error.\n\nThe issue may be known, or unknown at this time.\nPlease be patient and await further announcement.",
                          color = 0xff0000)
                e.set_footer(text=footer)
                try:
                    await ch.send(embed = e)
                except:
                    if g.id not in whitelist[BOT_CFG_FLAG]:
                        print(f"Server {g.name} not whitelisted. Passing.")
                        continue
            return
        case _:
            return


def u_restart():
    return
    scheduled_messages.append(True)
    return


async def get_uid(tid: str) -> str:
    return (await sql_select("uttcex_bot_db", "profiles", "discord_id", await stripid(tid)))[14]


async def discord_id_from_uid(uid: str) -> str:
    return (await sql_select("uttcex_bot_db", "profiles", "uttcex_id", await stripid(uid)))[0]


async def hardlock_bal(origin: str, coin: str, amount: str):
    """
    Lock a target ID's balance (for paid deductions on deposits / airdrops / etc)

    coin should always be base name like BTC or ETH, not nickname like satoshi or wei
    amount should always be whole coin values, never atomic amounts.
    """
    amount = format(Decimal(amount), decidic[coin])
    await sql_do("uttcex_bot_db",
                 f"INSERT INTO `locked_balance`(`origin`, `coin`, `amount`) VALUES ('{origin}','{coin}','{amount}');")
    return


async def hardunlock_bal(origin: str, coin: str, amount: str):
    """
    Unlock a target ID's balance (for repaying deductions of cancelled/incomplete deposits / airdrops / etc)

    coin should always be base name like BTC or ETH, not nickname like satoshi or wei
    amount should always be whole coin values, never atomic amounts.
    """
    amount = format(Decimal(amount), decidic[coin])
    await sql_do("uttcex_bot_db",
                 f"DELETE FROM `locked_balance` WHERE `origin` = '{origin}' AND `coin` = '{coin}' AND `amount` = '{amount}';")
    return

async def raw_lock_bal(origin: str, coin: str, amount: str) -> bool:
    data = await sql_select("uttcex_bot_db", "locked_balance", "*", "*")
    amount = format(Decimal(amount), decidic[coin])
    coin = coin.lower()
    if data is None: # User has not had any coins locked before, safe to just insert
        await sql_do("uttcex_bot_db", f"INSERT INTO `locked_balance`(`origin`, `coin`, `amount`) VALUES ('{origin}','{coin}','{amount}')")
        return True
    else:
        for bal in data:
            if bal[1] == coin.lower():
                new_bal = format(Decimal(bal[2]) + Decimal(amount), decidic[coin])
                await sql_do("uttcex_bot_db", f"UPDATE `locked_balance` SET `amount` = '{new_bal}' WHERE `origin` = '{origin}' AND `coin` = '{coin}'")
                return True
        # Didn't find coin, create
        await sql_do("uttcex_bot_db", f"INSERT INTO `locked_balance`(`origin`, `coin`, `amount`) VALUES ('{origin}','{coin}','{amount}')")
        return True
    return False

async def raw_unlock_bal(tid: str, coin: str, amount: str) -> bool:
    data = await sql_select("uttcex_bot_db", "locked_balance", "*", "*")
    amount = format(Decimal(amount), decidic[coin])
    coin = coin.lower()
    if data is None: # User has not had any coins locked before, do not unlock
        return False
    else:
        for bal in data:
            if bal[1] == coin.lower():
                new_bal = format(Decimal(bal[2]) - Decimal(amount), decidic[coin])
                await sql_do("uttcex_bot_db", f"UPDATE `locked_balance` SET `amount` = '{new_bal}' WHERE `origin` = '{tid}' AND `coin` = '{coin}'")
                return True
    return False

async def get_locked_balance(origin: str, coin: str):
    amounts = await sql_select("uttcex_bot_db", "locked_balance", "*", "*")
    locked = Decimal("0.0")
    if amounts is None:
        return locked
    else:
        for amount in amounts:
            if origin == "*":
                locked += Decimal(amount[2])
            if (amount[0] == origin or amount[0].find(str(origin)) != -1) and amount[1] == coin:
                locked += Decimal(amount[2])
        return locked

async def lock_bal(otype: str, tid: str, coin: str, amount: str):
    """
    Lock a target ID's balance (for paid deductions on deposits / airdrops / etc)

    coin should always be base name like BTC or ETH, not nickname like satoshi or wei
    amount should always be whole coin values, never atomic amounts.
    """
    bals = await sql_select("uttcex_bot_db", "locked_balance", "*", f"*")
    if bals is None:
        new_bal = format(Decimal(amount), decidic[coin])
        if otype == "":
            # Insert
            await sql_insert("uttcex_bot_db", "locked_balance", "origin", f"{tid}")
            await sql_update("uttcex_bot_db", "locked_balance", "amount", f"{new_bal}", "origin", f"{tid}")
            await sql_update("uttcex_bot_db", "locked_balance", "coin", coin, "origin", f"{tid}")
            return
        await sql_insert("uttcex_bot_db", "locked_balance", "origin", f"{otype}_{tid}")
        await sql_update("uttcex_bot_db", "locked_balance", "amount", f"{new_bal}", "origin", f"{otype}_{tid}")
        await sql_update("uttcex_bot_db", "locked_balance", "coin", coin, "origin", f"{otype}_{tid}")
        return
    else:
        for bal in bals:
            if otype == "":
                if (bal[0] == f"{tid}") and (coin == bal[2]):
                    new_bal = str(format(Decimal(bal[1]) + Decimal(amount), decidic[coin]))
                    await sql_update("uttcex_bot_db", "locked_balance", "amount", new_bal, "origin", f"{tid}")
                    return
            else:
                if (bal[0] == f"{otype}_{tid}") and (coin == bal[2]):
                    new_bal = str(format(Decimal(bal[1]) + Decimal(amount), decidic[coin]))
                    await sql_update("uttcex_bot_db", "locked_balance", "amount", new_bal, "origin", f"{otype}_{tid}")
                    return


async def unlock_bal(otype: str, tid: str, coin: str, amount: str):
    """
    Unlock a target ID's balance (for repaying deductions of cancelled/incomplete deposits / airdrops / etc)

    coin should always be base name like BTC or ETH, not nickname like satoshi or wei
    amount should always be whole coin values, never atomic amounts.
    """
    bals = await sql_select("uttcex_bot_db", "locked_balance", "*", f"*")
    for bal in bals:
        if otype == "":
            if (bal[0] == f"{tid}") and (coin == bal[2]):
                new_bal = str(format(Decimal(bal[1]) - Decimal(amount), decidic[coin]))
                await sql_update("uttcex_bot_db", "locked_balance", "amount", new_bal, "origin", f"{tid}")
                return
        else:
            if (bal[0] == f"{otype}_{tid}") and (coin == bal[2]):
                new_bal = str(format(Decimal(bal[1]) - Decimal(amount), decidic[coin]))
                await sql_update("uttcex_bot_db", "locked_balance", "amount", new_bal, "origin", f"{otype}_{tid}")
                return


async def backend_credit(target: int, amount: str, coin: str) -> None:
    uttcex_id = await get_uid(target)
    try:
        old_bal = Decimal((await sql_select(wallet_db[coin], coin, "key_name", uttcex_id))[4])
    except:
        old_bal = Decimal("0.0")
    new_bal = str(format(old_bal + amount, decidic[coin]))
    await sql_update(wallet_db[coin], coin, "instant_balance", new_bal, "key_name", uttcex_id)
    return


async def credit(msg: discord.Message):
    epc = 3
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (4):
            user = await stripid(p[1])
            amount = Decimal(p[2])  # ALWAYS USE WHOLE COIN AMOUNTS
            coin = p[3].lower()
            if (await has_profile(user) == True):  # Sanity check 1
                pass
            if (await has_wallet(user, coin) == True):  # Sanity check 2
                pass
            uttcex_id = await get_uid(user)
            old_bal = Decimal("0.0")
            old_bal = Decimal((await sql_select(wallet_db[coin], coin, "key_name", uttcex_id))[4])
            new_bal = str(format(amount + old_bal, decidic[coin]))
            await sql_update(wallet_db[coin], coin, "instant_balance", new_bal, "key_name", uttcex_id)
            e = discord.Embed(title=f"Credited {coin.upper()}",
                              description=f"The target `{user}` has been credited `{format(amount, decidic[coin])}` `{coin.upper()}` {emojis[coin]}",
                              color=coincolor[coin])
            await msg.reply(embed=e)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def mass_credit(msg: discord.Message):
    epc = 3
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (1):
            e = Embed(title = "Mass Credit Utility",
                      description = "Credit all users in local pending credit DB.\n\nUsage:\n`u.mass_credit <CDB filename>`",
                      color = 0xffffff)
            await msg.reply(embed = e)
            return
        case (2):
            s = ""
            with open(p[1], "r", encoding="utf-8") as f:
                f.seek(0)
                s = f.read()
                f.close()
            tmplist = list(s.split("\n"))
            new_list = []
            for x in tmplist:
                new_list.append(list(x.split(" ")))
            for entry in new_list:
                if (await has_wallet(int(entry[0])) is True):
                    pass
                else:
                    print("Failed wallet?")
                try:
                    await backend_credit(int(entry[0]), entry[1], entry[2])
                    print(f"Credited {entry[0]} {entry[1]} {entry[2]}")
                except:
                    print(f"Credit failed for {entry[0]}")
            print("Finished mass_credit")
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def mass_debit(msg: discord.Message):
    epc = 3
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (1):
            e = Embed(title = "Mass Debit Utility",
                      description = "Debit all users in local pending debit DB.\n\nUsage:\n`u.mass_credit <CDB filename>`\n\nWARNING - DOUBLE CHECK BEFORE PROCEEDING",
                      color = 0xffffff)
            await msg.reply(embed = e)
            return
        case (2):
            e = Embed(title = "Mass Debit Utility",
                      description = "Debit all users in local pending debit DB.\n\nUsage:\n`u.mass_credit <CDB filename>`\n\nWARNING - DOUBLE CHECK BEFORE PROCEEDING\n\nAre you sure? (yes/cancel) 15 seconds",
                      color = 0xffffff)
            await msg.reply(embed = e)
            def debit_confirm(msgx: discord.Message) -> bool:
                return msgx.author.id == msg.author.id and msgx.channel.id == msg.channel.id and msgx.content.lower() in ["yes", "cancel"]
            try:
                reply = await client.wait_for("message", check=debit_confirm, timeout=15)
            except asyncio.TimeoutError:
                await m.edit(content="Your command `mass_debit` has timed out.")
                return
            if reply.content.lower() == "yes" and reply.author.id == msg.author.id:
                # User confirmed, proceed with withdraw
                pass
            elif reply.content.lower() == "cancel" and reply.author.id == msg.author.id:
                await m.edit(content="Withdraw cancelled.", embed=None)
                return
            s = ""
            with open(p[1], "r", encoding="utf-8") as f:
                f.seek(0)
                s = f.read()
                f.close()
            tmplist = list(s.split("\n"))
            new_list = []
            for x in tmplist:
                new_list.append(list(x.split(" ")))
            for entry in new_list:
                if (await has_wallet(int(entry[0]), entry[2]) is True):
                    pass
                else:
                    print("Failed wallet?")
                try:
                    await backend_debit(int(entry[0]), entry[1], entry[2])
                    print(f"Credited {entry[0]} {entry[1]} {entry[2]}")
                except:
                    print(f"Credit failed for {entry[0]}")
            print("Finished mass_credit")
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def backend_debit(target: int, amount: str, coin: str) -> None:
    uttcex_id = await get_uid(target)
    old_bal = Decimal((await sql_select(wallet_db[coin], coin, "key_name", uttcex_id))[4])
    new_bal = str(format(old_bal - amount, decidic[coin]))
    await sql_update(wallet_db[coin], coin, "instant_balance", new_bal, "key_name", uttcex_id)
    return


async def debit(msg: discord.Message):
    epc = 3
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (4):
            user = await stripid(p[1])
            amount = Decimal(p[2])  # ALWAYS USE WHOLE COIN AMOUNTS
            coin = p[3].lower()
            if (await has_profile(user) == True):  # Sanity check 1
                pass
            if (await has_wallet(user, coin) == True):  # Sanity check 2
                pass
            uttcex_id = await get_uid(user)
            old_bal = Decimal("0.0")
            old_bal = Decimal((await sql_select(wallet_db[coin], coin, "key_name", uttcex_id))[4])
            new_bal = str(format(old_bal - amount, decidic[coin]))
            await sql_update(wallet_db[coin], coin, "instant_balance", new_bal, "key_name", uttcex_id)
            e = discord.Embed(title=f"Debited {coin.upper()}",
                              description=f"The target `{user}` has been debited `{format(amount, decidic[coin])}` `{coin.upper()}` {emojis[coin]}",
                              color=coincolor[coin])
            await msg.reply(embed=e)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def update_uttcex_bans(msg: discord.Message):
    c = 0
    s = 1
    for g in client.guilds:
        try:
            bans = g.bans()
            async for ban in bans:
                if (await has_profile(ban.user.id) == True):
                    if (await is_banned(ban.user.id) == False):
                        await sql_update("uttcex_bot_db", "profiles", "is_banned", "1", "discord_id", str(ban.user.id))
                        c += 1
            s += 1
        except:
            continue
    e = Embed(title = "Updated Bans", description = f"A total of **{c}** users in **{s}** servers have been added to the ban registry.\n\nPlease run this command once per week.", color = 0xff0000)
    await ereply(msg, e)
    return


async def dump(msg: discord.Message):
    epc = 0
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (3):  # Dump Info [u.dump info ID]
            if (p[1].lower() != "info"):
                await err(-1, [msg, f"Invalid parameter {p[1]}"])
                return
            discord_id = int(await stripid(p[2]))
            data1 = await sql_select("uttcex_bot_db", "profiles", "discord_id", str(discord_id))
            uttcex_id = data1[22]
            cl = await get_coin_list()
            data2 = []
            for coin in cl:
                if coin == "fluffy":
                    data2.append(await sql_select(wallet_db["sol"], "sol", "key_name", uttcex_id))
                else:
                    data2.append(await sql_select(wallet_db[coin], coin, "key_name", uttcex_id))
            try:
                data2.remove(None)
            except:
                pass
            e1 = discord.Embed(title=f"Profile Data of {discord_id}", description="\n".join(data1), color=0xffffff)
            s = ""
            for c in data2:
                if c is not None:
                    s += f"```\n" + "\n".join(c) + "```\n"
            e2 = discord.Embed(title=f"Wallet Data of {discord_id}", description=s, color=0xffffff)
            await edm(msg.author.id, e1)
            await edm(msg.author.id, e2)
            return
        case (4):  # Dump Key [u.dump key address coin]
            if (p[1].lower() != "key"):
                await err(-1, [msg, f"Invalid parameter {p[1]}"])
                return
            address = p[2].upper()
            coin = p[3].lower()
            key = ""
            try:
                key = (await sql_select(wallet_db[coin], coin, "public_address", address))[1]
            except:
                key = (await sql_select(wallet_db[coin], coin, "public_address", address.lower()))[1]
            await dm(msg.author.id, key)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return

last_2fa_time = 0
web2facode = ""

async def webadmin2fa(msg: discord.Message):
    global web2facode
    global last_2fa_time

    ctime = time.time()
    
    if last_2fa_time + 60 > ctime:
        s = f"{web2facode}\nTime remaining: {math.floor((last_2fa_time + 60) - ctime)} seconds."
        await msg.reply(s)
        return
    else:
        last_2fa_time = ctime
        web2facode = await rstr(8, 0)
        with open("C:\\xampp\\htdocs\\uttcex\\secure\\admin2fa.txt", "w") as f:
            f.write(web2facode)
            f.close()
        s = f"{web2facode}\nTime remaining: 60 seconds."
        await msg.reply(s)
        return

async def depcredit(msg: discord.Message):
    ouser = msg.author.id
    ochid = msg.channel.id
    epc = 4
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case 1:  # Help
            e = Embed(title = "Deposit Credit",
                      description = "**Usage:**\n`u.depcredit {Discord ID} {coin} {amount} {tx hash}`\n\n`{amount}` **must be atomic, ie: no decimals!**",
                      color = 0xffffff)
            await msg.reply(embed = e)
            return
        case 5: # cmd + Discord ID, coin, amount (atomic), tx hash
            try:
                user = int(await stripid(p[1]))
            except:
                await err(-1, [msg, "Cannot convert `user` to **int()** for ID."])
                return
            def depcredit_confirm(msg: discord.Message) -> bool:
                return msg.author.id == ouser and msg.channel.id == ochid and msg.content.lower() in ["yes", "cancel"]
            coin = p[2].lower()
            try:
                amount = await from_atomic(coin, int(p[3]))
            except:
                await err(-1, [msg, "Cannot convert `amount`."])
                return
            xamount = int(p[3])
            tx_hash = p[4]
            uid = await get_uid(user)
            addy = await udefs.udefs.get_address_from_uid(uid, coin)
            cmx = await msg.reply(f"Confirming information:\n> * **Recipient: <@{user}>**\n> * **Address: {addy}**\n> * **UTTCex ID:** `{uid}`\n> * **{amount}** {emojis[coin]}\n\n> * **TXID: {tx_hash}**\n\n> * Type `yes` to confirm.\n> * Type `cancel` to cancel.\n\nYou have 15 seconds to respond before this command times out.")
            try:
                reply = await client.wait_for("message", check=depcredit_confirm, timeout=15)
            except asyncio.TimeoutError:
                await cmx.edit(content = "Deposit credit has timed out.")
                return
            if reply.content.lower() == "yes" and reply.author.id == ouser:
                # User confirmed, proceed with staking
                await cmx.delete()  # Delete the confirmation message
            elif reply.content.lower() == "cancel" and reply.author.id == ouser:
                await cmx.delete()
                await ch.send("Deposit credit cancelled.")
                return
            data = await sql_select("mainnet", f"{coin}_utxos", "tx_hash", tx_hash)
            if data is not None:
                await msg.reply("This transaction already exists.")
                return
            await sql_do("mainnet", f"INSERT INTO `{coin}_utxos`(`receiving_address`, `tx_hash`, `key_name`, `atom_amount`) VALUES ('{addy}','{tx_hash}','{uid}','{xamount}')")
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return

async def noreply(msg: discord.Message):
    chid = str(msg.channel.id)
    epc = 1
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case 1:  # Help
            e = Embed(title = "No Reply Channels",
                      description = "**Usage:**\n`u.noreply {on/off}`\n\nToggles UTTCex's ability to respond in this channel.",
                      color = 0xffffff)
            await msg.reply(embed = e)
            return
        case 2:
            match p[1].lower():
                case "on":
                    data = await sql_select("uttcex_bot_db", "no_reply", "channel_id", chid)
                    if data is None: # Doesn't exist
                        await sql_insert("uttcex_bot_db", "no_reply", "channel_id", chid)
                        await sql_update("uttcex_bot_db", "no_reply", "flag", "1", "channel_id", chid)
                        await msg.reply("Channel is now marked as no-reply.\nUTTCex will not respond to commands here.")
                        return
                    else: # Does exist
                        await sql_update("uttcex_bot_db", "no_reply", "flag", "1", "channel_id", chid)
                        await msg.reply("Channel is now marked as no-reply.\nUTTCex will not respond to commands here.")
                        return
                    return
                case "off":
                    data = await sql_select("uttcex_bot_db", "no_reply", "channel_id", chid)
                    if data is None: # Doesn't exist
                        await sql_insert("uttcex_bot_db", "no_reply", "channel_id", chid)
                        await sql_update("uttcex_bot_db", "no_reply", "flag", "0", "channel_id", chid)
                        await msg.reply("UTTCex will now respond in this channel.")
                        return
                    else: # Does exist
                        await sql_update("uttcex_bot_db", "no_reply", "flag", "0", "channel_id", chid)
                        await msg.reply("UTTCex will now respond in this channel.")
                        return
                    return
                case _:
                    await msg.reply("Invalid switch.")
                    return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def isnoreply(msg: discord.Message):
    chid = str(msg.channel.id)
    data = await sql_select("uttcex_bot_db", "no_reply", "channel_id", chid)
    if data is None: # Doesn't exist
        await msg.reply("UTTCex can respond to commands in this channel.")
        return
    else:
        if data[1] == "1":
            await msg.reply("UTTCex is marked as no-reply for commands in this channel.")
            return
        elif data[1] == "0":
            await msg.reply("UTTCex can respond to commands in this channel.")
            return


async def announce(msg: discord.Message):
    atxt = msg.content[10:]
    e = Embed(title = "UTTCex Announcement",
              description = "",
              color = 0xffffff)
    e.set_footer(text=await timestamp())
    data = await sql_select("uttcex_bot_db", "servers", "*", "*")
    for entry in data:
        ch = client.get_channel(int(entry[3]))
        try:
            e.description = f"Dear <@{entry[1]}>,\nCC: All UTTCex Hosts & Server Owners\n\n{atxt}\n\nRegards, <@{msg.author.id}>"
            await ch.send(embed = e)
        except:
            continue
    return
# Admins #

# Misc #


# Tests #
async def do_sql_sel(msg: discord.Message):
    epc = 4
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (5):
            data = await sql_select(p[1], p[2], p[3], p[4])
            if data is None:
                await err(5, [msg])
                return
            await reply(msg, data[0])
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return
    return


async def do_sql_upd(msg: discord.Message):
    epc = 7
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (5):
            await sql_update(p[1], p[2], p[3], p[4], p[5], p[6], p[7])
            data = await sql_select(p[1], p[2], p[3], p[4])
            if data is None:
                await err(5, [msg])
                return
            await reply(msg, data)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return
    return


async def auth_test(msg: discord.Message):
    epc = 1
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    pg = len(p) - 1
    match (len(p)):
        case (2):
            auth = await get_auth(msg.author.id)
            if auth >= int(p[1]):
                e = discord.Embed(title="Authorized", description=f"You meet the authorization level `{p[1]}`.",
                                  color=0x00ff00)
                await ereply(msg, e)
                return
            e = discord.Embed(title="Unauthorized", description=f"You do not meet the authorization level `{p[1]}`.",
                              color=0xff0000)
            await ereply(msg, e)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def q_discrepancy(coin: str) -> bool:
    instant_bals = await sql_select(wallet_db[coin], coin, "instant_balance", "*")
    ax = False
    ay = False
    if (instant_bals == None):
        ax = True
    else:
        try:
            for bal in instant_bals:
                cred += Decimal(bal)
        except:
            cred = Decimal(0.0)
    cred = Decimal(0.0)
    for bal in instant_bals:
        cred += Decimal(bal)
    utxo_bals = []
    try:
        utxo_bals = t_sql_select(wallet_db[coin], f"{coin}_utxos", "sat_amount", "*")
    except:
        utxo_bals = t_sql_select(wallet_db[coin], f"{coin}_utxos", "atom_amount", "*")
    real = Decimal(0.0)
    if (utxo_bals == None):
        ay = True
    else:
        for bal in utxo_bals:
            real += Decimal(format(t_from_atomic(coin, int(bal)), decidic[coin]))
    disc = Decimal(real - (cred + locked))
    if ((format(float(abs(disc)), decidic[coin])) == (format(0.0, decidic[coin]))):
        return False
    elif (format(float(abs(disc)), decidic[coin]) != (format(0.0, decidic[coin]))):
        clx = 0xff0000
        if ((real - cred) > 0):
            return True
        elif ((real - cred) < 0):
            return True
        else:
            return False


async def discrepancy(msg: discord.Message):
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    epc = 1
    match (len(p)):
        case (2):
            coin = p[1].lower()
            if (coin == "showall"):
                r = ""
                for xcoin in (await get_coin_list()):
                    try:
                        if ((await q_discrepancy(xcoin)) == True):
                            r += f"{emojis[xcoin]} {xcoin.upper()} - `True`\n"
                    except:
                        continue
                if r == "":
                    e = discord.Embed(title="Quick Discrepancy", description="None found!", color=0xffffff)
                    await ereply(msg, e)
                    return
                else:
                    e = discord.Embed(title="Quick Discrepancy", description=r, color=0xffffff)
                    await ereply(msg, e)
                    return
            locked = await get_locked_balance("*", coin)
            bx = False
            if (locked == Decimal("0.0")):
                bx = True
            else:
                pass
            instant_bals = None
            instant_bals = await sql_select(wallet_db[coin], coin, "instant_balance", "*")
            ax = False
            ay = False
            cred = Decimal("0.0")
            if (instant_bals == None):
                ax = True
            else:
                for bal in instant_bals:
                    if bal == "":
                        bal = Decimal("0.0")
                    cred += Decimal(bal)
            utxo_bals = []
            utxo_bals = await sql_select(wallet_db[coin], f"{coin}_utxos", "atom_amount", "*")
            real = Decimal(0.0)
            if (utxo_bals == None):
                ay = True
            else:
                for bal in utxo_bals:
                    if bal == "":
                        bal = Decimal("0.0")
                    real += Decimal(format(t_from_atomic(coin, int(bal)), decidic[coin]))
            disc = Decimal(real - cred)
            clx = 0xff0000
            e = None
            if ((format(float(abs(disc)), decidic[coin])) == (format(0.0, decidic[coin]))):
                e = discord.Embed(title=f"{coin.upper()} Discrepancy Check",
                                  description=f"Internal: `{format(real, decidic[coin])}`\nInstant: `{format(cred, decidic[coin])}`\nLocked: `{format(locked, decidic[coin])}`\n\nDiscrepancy: `None`",
                                  color=coincolor[coin])
            elif (format(float(abs(disc)), decidic[coin]) != (format(0.0, decidic[coin]))):
                clx = 0xff0000
                if ((real - cred) > 0):
                    e = discord.Embed(title=f"{coin.upper()} Discrepancy Check",
                                      description=f"Internal: `{format(real, decidic[coin])}`\nInstant: `{format(cred, decidic[coin])}`\nDiscrepancy: `-{format(real - cred, decidic[coin])}`",
                                      color=clx)
                elif ((real - cred) < 0):
                    e = discord.Embed(title=f"{coin.upper()} Discrepancy Check",
                                      description=f"Internal: `{format(real, decidic[coin])}`\nInstant: `{format(cred, decidic[coin])}`\nDiscrepancy: `+{format(abs(real - cred), decidic[coin])}`",
                                      color=clx)
                else:
                    e = discord.Embed(title=f"{coin.upper()} Discrepancy Check",
                                      description=f"Internal: `{format(real, decidic[coin])}`\nInstant: `{format(cred, decidic[coin])}`\nLocked: `{format(locked, decidic[coin])}`\n\nDiscrepancy: `None`",
                                      color=coincolor[coin])
            await ereply(msg, e)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def grabmsgsfromch(msg: discord.Message):
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    epc = 1
    match (len(p)):
        case (1): # Help
            e = Embed(title = "Grab messages from a channel:",
                      description = "`u.gmfc {C-ID}`",
                      color = 0xffffff)
            await msg.reply(embed = e)
            return
        case (2):
            x = await msg.reply("Grabbing messages ...")
            channel = client.get_channel(int(p[1]))
            ch = msg.channel.id
            
            if not channel:
                await x.edit(content = f"Channel with ID {ch} not found.")
                return
            messages = []
            async for message in channel.history(limit=None, oldest_first=True):
                messages.append(message)
            s = ""
            sx = 0
            t = ""
            tx = 0
            await x.edit(content = f"Messages received.")
            for message in messages:
                for emb in message.embeds:
                    t += str(msg.author.id) + f" Embed - (Title: {emb.title}) {emb.description}" + "\n"
                    tx += 1
                try:
                    s += str(msg.author.id) + " " + message.content + "\n"
                    sx += 1
                except:
                    continue
            await x.edit(content = "Writing messages to file ...")
            with open(f"grab_messages_{p[1]}.txt", "w", encoding='utf-8') as f:
                f.write(s)
                f.close()
            with open(f"grab_embeds_{p[1]}.txt", "w", encoding='utf-8') as f:
                f.write(t)
                f.close()
            await x.edit(content = f"Wrote messages. Total: {len(messages)} messages, {sx - tx} plaintext, {tx} embedded.\nCheck console for balance list.")
            await parse_grabbed_msgs(f"grab_messages_{p[1]}.txt")
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def parse_grabbed_msgs(filename: str):
    data = ""
    with open(filename, "r", encoding="utf-8") as f:
        f.seek(0)
        data = f.read()
        f.close()
    data = list(data.split("\n"))
    balance_list = []
    for x in data:
        if x == "":
            continue
        tmp = x.lower()
        if tmp.find("u.tip") != -1: # Tip found
            tmplist = list(tmp.split(" "))
            sender = tmplist[0]
            try:
                receiver = await stripid(tmplist[2])
            except:
                continue
            amount = tmplist[3]
            coin = tmplist[4]
            try:
                balance_list.append([sender, receiver, Decimal(amount), coin])
            except:
                print(receiver)
                continue
    aggregated = defaultdict(lambda: defaultdict(Decimal))
    for sender, receiver, amount, coin in balance_list:
        aggregated[receiver][coin] += amount
    result_list = []
    for receiver, coins in aggregated.items():
        for coin, amount in coins.items():
            result_list.append([receiver, amount, coin])
    s = ""
    for x in result_list:
        s += f"{x[0]} {x[1]} {x[2]}\n"
    with open(filename, "w", encoding="utf-8") as f:
        f.seek(0)
        f.write(s)
        f.close()
    coin_totals = defaultdict(Decimal)
    for recipient, amount, coin in result_list:
        coin_totals[coin] += amount
    print(coin_totals["btc"])
    print(coin_totals["sat"])
    print(coin_totals["bnb"])
    print(coin_totals["fluffy"])
    print(coin_totals["usdt"])
    print(coin_totals["matic"])
    return


async def import_banlist(msg: discord.Message):
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    epc = 1
    match (len(p)):
        case (1): # Help
            e = Embed(title = "Import a _banlist.blt:",
                      description = "`u.import_banlist \"name\"`",
                      color = 0xffffff)
            await msg.reply(embed = e)
            return
        case (2):
            with open(f"{p[1]}_banlist.blt", "r") as f:
                f.seek(0)
                data = f.read()
                id_list = list(data.split("\n"))
                c = 0
                for did in id_list:
                    if (await has_profile(int(did))) is True:
                        pass # Sanity Check
                    await sql_update("uttcex_bot_db", "profiles", "is_banned", "1", "discord_id", did)
                    await sql_update("uttcex_bot_db", "profiles", "ban_reason", "Known Scammer", "discord_id", did)
                    c += 1
                e = Embed(title = f"Banned from list \"{p[1]}\"",
                          description = f"{c} users banned.",
                          color = 0xff0000)
                await msg.reply(embed = e)
                return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


async def check_bal(msg: discord.Message):
    p = await sanistr(msg.content.replace("  ", " "))
    p = list(msg.content.split(" "))
    epc = 1
    match (len(p)):
        case (1): # Help
            e = Embed(title = "Import a _banlist.blt:",
                      description = "`u.import_banlist \"name\"`",
                      color = 0xffffff)
            await msg.reply(embed = e)
            return
        case (3):
            user = await stripid(p[1])
            coin = ""
            try:
                coin = alias[p[2].lower()]
            except:
                await err(17, [msg])
            if p[1].startswith("uid:"):
                user = p[1].replace("uid:","")
                data = await sql_select("mainnet", coin, "key_name", user)
                e = Embed(title = "Balance of:",
                          description = f"UTTCexID: {user} >> {data[4]} {emojis[coin]}",
                          color = coincolor[coin])
            else:
                if (await has_wallet(user, coin)) is True:
                    pass
                data = await sql_select("mainnet", coin, "key_name", await get_uid(user))
                e = Embed(title = "Balance of:",
                          description = f"<@{user}> {data[4]} {emojis[coin]}",
                          color = coincolor[coin])
            await msg.reply(embed = e)
            return
        case _:
            await err(2, [msg, msg.content, epc, pg])
            return


if __name__ == "__main__":
    main()
    exit(0)
