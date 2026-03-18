from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3, hashlib, json, time, os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB_PATH = os.environ.get("DB_PATH", "game.db")

HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Realm of Shadows</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#080810;color:#d4c9a8;font-family:'Segoe UI',Arial,sans-serif;min-height:100vh;font-size:14px;overflow-x:hidden}
:root{--gold:#c9a227;--purple:#5c3d8f;--red:#c0392b;--green:#27ae60;--blue:#2980b9;--dark:#0d0d18;--card:#12121e;--border:#2a2540}
#root{max-width:1040px;margin:0 auto;padding:8px}

/* AUTH */
#auth-screen{display:flex;align-items:center;justify-content:center;min-height:95vh;background:radial-gradient(ellipse at center,#1a0a2e 0%,#080810 70%)}
.auth-card{background:#12121e;border:1px solid #3a2560;border-radius:16px;padding:32px;width:100%;max-width:360px;text-align:center;box-shadow:0 0 40px rgba(92,61,143,.3)}
.auth-logo{font-size:32px;margin-bottom:6px}
.auth-title{font-size:22px;font-weight:bold;color:var(--gold);margin-bottom:4px;letter-spacing:2px}
.auth-sub{color:#555;font-size:12px;margin-bottom:22px}
.auth-tabs{display:flex;margin-bottom:16px;background:#0a0a0f;border-radius:8px;padding:3px;gap:3px}
.atab{flex:1;padding:7px;border:none;background:transparent;color:#555;cursor:pointer;border-radius:6px;font-size:13px;font-weight:bold}
.atab.on{background:var(--purple);color:#fff}
.finp{width:100%;padding:10px 12px;border-radius:8px;border:1px solid #2a2540;background:#0d0d18;color:#d4c9a8;font-size:14px;outline:none;margin-bottom:9px;display:block}
.finp:focus{border-color:var(--purple)}
.fbtn{width:100%;padding:12px;border-radius:9px;border:none;background:var(--purple);color:#fff;font-size:15px;font-weight:bold;cursor:pointer;transition:background .15s}
.fbtn:hover{background:#7450b0}
.fbtn:disabled{opacity:.5;cursor:not-allowed}
.ferr{color:#e74c3c;font-size:13px;margin-top:8px;min-height:18px}

/* HEADER */
#hdr{background:linear-gradient(135deg,#12121e,#1a1030);border-radius:12px;padding:10px 14px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;border:1px solid var(--border)}
.hdr-l{display:flex;flex-direction:column;gap:3px}
#hdr-name{font-size:15px;font-weight:bold;color:var(--gold);letter-spacing:1px}
.hdr-bars{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.hbar-wrap{display:flex;align-items:center;gap:5px}
.hbar-label{font-size:10px;color:#555;text-transform:uppercase;letter-spacing:.04em;width:18px}
.hbar-bg{width:90px;height:8px;background:#1a1a2e;border-radius:4px;overflow:hidden}
.hbar-fill{height:8px;border-radius:4px;transition:width .4s}
.hbar-hp{background:linear-gradient(90deg,#8b2020,#e74c3c)}
.hbar-xp{background:linear-gradient(90deg,#3d1a6e,#9b59b6)}
.hbar-text{font-size:11px;color:#888;min-width:60px}
.hdr-stats{display:flex;gap:10px;flex-wrap:wrap;margin-top:2px}
.hstat{font-size:12px;color:#666}
.hstat b{color:#d4c9a8}
.hbtns{display:flex;gap:5px;align-items:center;flex-wrap:wrap}
.hbtn{padding:5px 11px;border-radius:7px;border:1px solid var(--border);background:transparent;color:#888;cursor:pointer;font-size:11px;transition:all .12s}
.hbtn:hover{border-color:var(--gold);color:var(--gold)}
.hbtn.red:hover{border-color:#e74c3c;color:#e74c3c}
.sdot{display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--green);margin-left:4px;vertical-align:middle;opacity:0;transition:opacity .4s}
.sdot.on{opacity:1}

/* TABS */
#tabs{display:flex;gap:4px;margin-bottom:8px;background:#12121e;padding:4px;border-radius:10px;border:1px solid var(--border);flex-wrap:wrap}
.tab{flex:1;min-width:52px;padding:6px 3px;border-radius:7px;border:none;background:transparent;color:#555;cursor:pointer;font-size:11px;font-weight:bold;transition:all .12s}
.tab:hover{background:#1a1a2e;color:#aaa}
.tab.on{background:var(--purple);color:#fff}
.panel{display:none}

/* ═══════════════════════════════════════════════
   WORLD MAP
═══════════════════════════════════════════════ */
#p-world{flex-direction:column;gap:0}
#world-map-wrap{position:relative;width:100%;background:var(--card);border-radius:12px;border:1px solid var(--border);overflow:hidden;margin-bottom:10px}
#world-svg{width:100%;display:block}
.map-zone-btn{cursor:pointer;transition:all .2s}
.map-zone-btn:hover .zone-glow{opacity:.8}
.map-zone-btn.locked{opacity:.4;cursor:not-allowed}
.zone-glow{opacity:.3;transition:opacity .3s}
.zone-pulse{animation:zpulse 2s ease-in-out infinite}
@keyframes zpulse{0%,100%{opacity:.3}50%{opacity:.7}}
.zone-active .zone-glow{opacity:.9;animation:zpulse 1.5s ease-in-out infinite}
#map-tooltip{position:absolute;background:#1a1a2e;border:1px solid var(--border);border-radius:8px;padding:8px 12px;font-size:12px;pointer-events:none;display:none;z-index:10;max-width:160px}
#map-tooltip b{color:var(--gold);display:block;margin-bottom:3px}

/* ═══════════════════════════════════════════════
   BATTLE
═══════════════════════════════════════════════ */
#p-battle{flex-direction:column;gap:8px}
.battle-scene{background:var(--card);border-radius:12px;border:1px solid var(--border);overflow:hidden;position:relative}
.battle-bg{width:100%;height:220px;position:relative;display:flex;align-items:flex-end;justify-content:space-between;padding:0 40px 20px}
/* Zone backgrounds */
.bg-forest{background:linear-gradient(180deg,#0a1a0a 0%,#0d2010 40%,#1a3010 100%)}
.bg-cave{background:linear-gradient(180deg,#0a0a0a 0%,#101018 40%,#1a1828 100%)}
.bg-ruins{background:linear-gradient(180deg,#1a100a 0%,#2a1810 40%,#1a1208 100%)}
.bg-volcano{background:linear-gradient(180deg,#1a0800 0%,#2a0e00 40%,#3a1400 100%)}
.bg-abyss{background:linear-gradient(180deg,#08000f 0%,#100020 40%,#0a0015 100%)}
/* Parallax decorations */
.battle-deco{position:absolute;pointer-events:none}
/* Player sprite */
.player-sprite{position:relative;z-index:3;display:flex;flex-direction:column;align-items:center;gap:4px}
.sprite-body{font-size:52px;line-height:1;filter:drop-shadow(0 4px 8px rgba(0,0,0,.8));transition:transform .15s}
.sprite-body.attack-anim{animation:atk-anim .4s ease-out}
.sprite-body.hurt-anim{animation:hurt-anim .3s ease-out}
@keyframes atk-anim{0%{transform:translateX(0)}30%{transform:translateX(60px) scale(1.2)}60%{transform:translateX(30px)}100%{transform:translateX(0)}}
@keyframes hurt-anim{0%,100%{transform:translateX(0);filter:drop-shadow(0 4px 8px rgba(0,0,0,.8))}50%{transform:translateX(-8px);filter:drop-shadow(0 0 16px rgba(231,76,60,1)) brightness(2)}}
.sprite-name{font-size:11px;color:#aaa;font-weight:bold;background:rgba(0,0,0,.5);padding:2px 6px;border-radius:4px}
/* Enemy sprite */
.enemy-sprite{position:relative;z-index:3;display:flex;flex-direction:column;align-items:center;gap:4px}
.enemy-body{font-size:60px;line-height:1;filter:drop-shadow(0 4px 12px rgba(0,0,0,.9));transition:transform .15s;transform:scaleX(-1)}
.enemy-body.attack-anim{animation:eatk-anim .4s ease-out}
.enemy-body.hurt-anim{animation:ehurt-anim .3s ease-out}
@keyframes eatk-anim{0%{transform:scaleX(-1) translateX(0)}30%{transform:scaleX(-1) translateX(60px) scale(1.15)}100%{transform:scaleX(-1) translateX(0)}}
@keyframes ehurt-anim{0%,100%{transform:scaleX(-1);filter:drop-shadow(0 4px 12px rgba(0,0,0,.9))}50%{transform:scaleX(-1) translateX(8px);filter:drop-shadow(0 0 20px rgba(231,76,60,1)) brightness(2.5)}}
/* HP bars in battle scene */
.battle-hpbars{display:grid;grid-template-columns:1fr auto 1fr;gap:8px;align-items:center;padding:10px 14px;border-top:1px solid var(--border)}
.bhp-block{display:flex;flex-direction:column;gap:3px}
.bhp-block.enemy-side{align-items:flex-end}
.bhp-name{font-size:12px;font-weight:bold;color:#d4c9a8}
.bhp-val{font-size:11px;color:#777}
.bhp-bar-bg{height:10px;background:#1a1a2e;border-radius:5px;overflow:hidden}
.bhp-bar{height:10px;border-radius:5px;transition:width .4s}
.bhp-p{background:linear-gradient(90deg,var(--green),#2ecc71)}
.bhp-e{background:linear-gradient(90deg,#8b2020,var(--red))}
.vs-badge{background:#1a1a2e;border:1px solid var(--border);border-radius:8px;padding:6px 10px;font-size:13px;font-weight:bold;color:#555;text-align:center;flex-shrink:0}
/* Floating damage numbers */
.dmg-float{position:absolute;font-size:18px;font-weight:bold;pointer-events:none;animation:float-up .9s ease-out forwards;z-index:20;text-shadow:0 2px 4px rgba(0,0,0,.9)}
.dmg-player{color:#e74c3c}
.dmg-enemy{color:#ffd166}
.dmg-crit{font-size:24px;color:#ff6b6b}
.dmg-heal{color:#2ecc71}
@keyframes float-up{0%{opacity:1;transform:translateY(0) scale(1)}100%{opacity:0;transform:translateY(-70px) scale(.7)}}
/* Battle log */
.battle-log-wrap{background:#0a0a0f;border-top:1px solid var(--border);padding:8px 12px;height:100px;overflow-y:auto;font-size:12px}
.battle-log-wrap::-webkit-scrollbar{width:3px}
.battle-log-wrap::-webkit-scrollbar-thumb{background:#333;border-radius:2px}
.blog{padding:1px 0;line-height:1.6}
.blog.atk{color:#e67e22}.blog.def{color:#3498db}.blog.crit{color:#ff6b6b;font-weight:bold}
.blog.loot{color:var(--gold);font-weight:bold}.blog.xp{color:#9b59b6}
.blog.die{color:var(--red)}.blog.heal{color:var(--green)}.blog.sys{color:#555}
/* Battle actions */
.battle-actions{display:flex;gap:6px;flex-wrap:wrap;padding:10px 14px;border-top:1px solid var(--border)}
.bact{flex:1;min-width:80px;padding:9px 6px;border-radius:9px;border:none;font-size:13px;font-weight:bold;cursor:pointer;transition:all .1s;position:relative;overflow:hidden}
.bact:active:not([disabled]){transform:scale(.95)}
.bact[disabled]{opacity:.35;cursor:not-allowed}
.bact-atk{background:linear-gradient(135deg,#6b1515,#8b2020);color:#ffa0a0;border:1px solid #a03030}
.bact-atk:hover:not([disabled]){background:linear-gradient(135deg,#8b2020,#c0392b)}
.bact-skill{background:linear-gradient(135deg,#1a2d6b,#1e4d7b);color:#80b0ff;border:1px solid #2a5d9b}
.bact-skill:hover:not([disabled]){background:linear-gradient(135deg,#1e4d7b,#2980b9)}
.bact-heal{background:linear-gradient(135deg,#0d3d1a,#1a5c28);color:#80ff90;border:1px solid #2a7c38}
.bact-heal:hover:not([disabled]){background:linear-gradient(135deg,#1a5c28,var(--green))}
.bact-flee{background:#1a1a2e;color:#777;border:1px solid #333}
.bact-flee:hover:not([disabled]){background:#222;color:#aaa}
.skill-cd{font-size:9px;opacity:.7;display:block;margin-top:1px}
.battle-idle-msg{text-align:center;padding:50px 20px;color:#444;font-size:14px}

/* ═══════════════════════════════════════════════
   INVENTORY — 8 SLOTS
═══════════════════════════════════════════════ */
#p-inv{display:grid;grid-template-columns:280px 1fr;gap:10px}
.inv-left{display:flex;flex-direction:column;gap:8px}
.char-preview{background:var(--card);border-radius:12px;border:1px solid var(--border);padding:14px;text-align:center}
.char-avatar{font-size:56px;margin:8px 0;filter:drop-shadow(0 4px 12px rgba(0,0,0,.8))}
.char-name{font-size:14px;font-weight:bold;color:var(--gold);margin-bottom:8px}
.equip-mannequin{display:grid;grid-template-columns:1fr 60px 1fr;grid-template-rows:repeat(4,52px);gap:5px;max-width:220px;margin:0 auto}
.eq-slot{background:#0d0d18;border:1px solid #2a2540;border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:4px;cursor:pointer;transition:border-color .15s;position:relative;min-height:52px}
.eq-slot:hover{border-color:var(--purple)}
.eq-slot.has-item{border-color:#3a3060}
.eq-slot-label{font-size:8px;color:#333;text-transform:uppercase;letter-spacing:.04em;margin-bottom:2px}
.eq-slot-icon{font-size:20px;line-height:1}
.eq-slot-name{font-size:8px;color:#888;margin-top:1px;max-width:60px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:center}
.eq-slot-empty{font-size:16px;color:#222}
.eq-center{display:flex;align-items:center;justify-content:center}
.stats-mini{background:var(--card);border-radius:10px;border:1px solid var(--border);padding:10px}
.stats-mini h4{font-size:10px;color:#555;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px}
.stat-row{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid #1a1a2e;font-size:12px}
.stat-row:last-child{border-bottom:none}
.stat-row-label{color:#666}
.stat-row-val{font-weight:bold;color:#d4c9a8}
.stat-row-val.bonus{color:var(--green)}
/* Inventory list */
.inv-right{background:var(--card);border-radius:12px;border:1px solid var(--border);padding:12px}
.inv-right h3{font-size:11px;color:#555;text-transform:uppercase;letter-spacing:.07em;margin-bottom:8px;display:flex;justify-content:space-between}
.inv-sort{display:flex;gap:4px;margin-bottom:8px}
.sort-btn{padding:3px 8px;border-radius:5px;border:1px solid var(--border);background:transparent;color:#666;font-size:10px;cursor:pointer}
.sort-btn.on{background:var(--purple);color:#fff;border-color:var(--purple)}
.item-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(56px,1fr));gap:6px;max-height:420px;overflow-y:auto}
.item-grid::-webkit-scrollbar{width:3px}
.item-grid::-webkit-scrollbar-thumb{background:#333;border-radius:2px}
.item-cell{background:#0d0d18;border-radius:8px;border:2px solid #1a1a2e;padding:6px;display:flex;flex-direction:column;align-items:center;gap:2px;cursor:pointer;transition:all .12s;aspect-ratio:1;position:relative}
.item-cell:hover{transform:scale(1.05);z-index:2}
.item-cell.equipped{border-color:var(--green)}
.item-cell-icon{font-size:22px;line-height:1}
.item-cell-name{font-size:8px;text-align:center;color:#888;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;max-width:100%}
/* rarity borders */
.rc-common{border-color:#333}.rc-uncommon{border-color:#27ae60}.rc-rare{border-color:#3498db}
.rc-epic{border-color:#9b59b6}.rc-legendary{border-color:#e67e22}.rc-mythic{border-color:#e74c3c;box-shadow:0 0 8px rgba(231,76,60,.4)}

/* rarity text colors */
.r-common{color:#aaa}.r-uncommon{color:#27ae60}.r-rare{color:#3498db}
.r-epic{color:#9b59b6}.r-legendary{color:#e67e22}.r-mythic{color:#e74c3c}
.badge-common{background:#222;color:#aaa}.badge-uncommon{background:#1a3d1a;color:#27ae60}
.badge-rare{background:#1a2d3d;color:#3498db}.badge-epic{background:#2d1a3d;color:#9b59b6}
.badge-legendary{background:#3d2a1a;color:#e67e22}.badge-mythic{background:#3d1a1a;color:#e74c3c}

/* ═══════════════════════════════════════════════
   TALENTS
═══════════════════════════════════════════════ */
#p-talents{display:flex;flex-direction:column;gap:10px}
.talent-header{background:var(--card);border-radius:12px;border:1px solid var(--border);padding:14px;display:flex;align-items:center;gap:14px}
.talent-pts{font-size:28px;font-weight:bold;color:var(--gold)}
.talent-pts-label{font-size:12px;color:#666}
.talent-tree{background:var(--card);border-radius:12px;border:1px solid var(--border);padding:14px}
.talent-branch{margin-bottom:16px}
.talent-branch-title{font-size:11px;color:#555;text-transform:uppercase;letter-spacing:.07em;margin-bottom:8px;padding-bottom:5px;border-bottom:1px solid var(--border)}
.talent-row{display:flex;flex-wrap:wrap;gap:8px}
.talent-node{background:#0d0d18;border:1px solid var(--border);border-radius:10px;padding:10px;width:140px;cursor:pointer;transition:all .15s;position:relative}
.talent-node:hover:not(.locked-talent){border-color:var(--purple);background:#12101e}
.talent-node.unlocked{border-color:var(--gold);background:#1a1408}
.talent-node.locked-talent{opacity:.4;cursor:not-allowed}
.talent-node-icon{font-size:24px;margin-bottom:4px}
.talent-node-name{font-size:12px;font-weight:bold;color:#d4c9a8;margin-bottom:2px}
.talent-node-desc{font-size:10px;color:#666;line-height:1.4}
.talent-node-cost{font-size:10px;color:var(--gold);margin-top:4px}
.talent-node-lvl{position:absolute;top:6px;right:6px;font-size:9px;background:var(--purple);color:#fff;padding:1px 5px;border-radius:3px}

/* ═══════════════════════════════════════════════
   SHOP / CASES
═══════════════════════════════════════════════ */
#p-shop{display:flex;flex-direction:column;gap:10px}
.shop-balance{background:var(--card);border-radius:12px;border:1px solid var(--border);padding:12px 16px;display:flex;align-items:center;gap:10px}
.shop-gold{font-size:22px;font-weight:bold;color:var(--gold)}
.cases-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}
.case-card{background:var(--card);border-radius:12px;border:1px solid var(--border);padding:16px;text-align:center;cursor:pointer;transition:all .15s;position:relative;overflow:hidden}
.case-card:hover{border-color:var(--purple);transform:translateY(-2px)}
.case-card::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(92,61,143,.05),transparent);pointer-events:none}
.case-icon{font-size:48px;margin:8px 0;filter:drop-shadow(0 4px 12px rgba(0,0,0,.8))}
.case-name{font-size:14px;font-weight:bold;color:#d4c9a8;margin-bottom:4px}
.case-desc{font-size:11px;color:#555;margin-bottom:10px;line-height:1.5}
.case-contents{display:flex;gap:4px;flex-wrap:wrap;justify-content:center;margin-bottom:10px}
.case-rarity-badge{font-size:9px;padding:2px 6px;border-radius:3px;font-weight:bold}
.case-price{font-size:15px;font-weight:bold;color:var(--gold);margin-bottom:8px}
.case-open-btn{width:100%;padding:9px;border-radius:8px;border:none;background:var(--purple);color:#fff;font-size:13px;font-weight:bold;cursor:pointer;transition:background .12s}
.case-open-btn:hover{background:#7450b0}
.case-open-btn:disabled{opacity:.4;cursor:not-allowed}

/* Case opening animation */
#case-modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.85);display:none;align-items:center;justify-content:center;z-index:200;flex-direction:column;gap:20px}
#case-modal-bg.on{display:flex}
.case-reel-wrap{width:min(600px,95vw);overflow:hidden;border-radius:12px;border:2px solid var(--border);position:relative}
.case-reel-inner{display:flex;gap:6px;padding:8px;background:#0a0a0f;transition:transform .0s}
.case-reel-inner.spinning{transition:transform 3.5s cubic-bezier(0.15,0.85,0.3,1)}
.reel-item{flex-shrink:0;width:100px;height:100px;border-radius:10px;border:2px solid #2a2540;background:#12121e;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px}
.reel-item-icon{font-size:32px}
.reel-item-name{font-size:9px;text-align:center;color:#888;padding:0 4px}
.case-reel-arrow{position:absolute;top:0;bottom:0;left:50%;width:2px;background:var(--gold);transform:translateX(-50%);z-index:5;pointer-events:none}
.case-reel-arrow::before,.case-reel-arrow::after{content:'';position:absolute;left:50%;transform:translateX(-50%);width:0;height:0}
.case-reel-arrow::before{top:0;border-left:8px solid transparent;border-right:8px solid transparent;border-top:14px solid var(--gold)}
.case-reel-arrow::after{bottom:0;border-left:8px solid transparent;border-right:8px solid transparent;border-bottom:14px solid var(--gold)}
.case-result-reveal{text-align:center;animation:reveal-pop .5s cubic-bezier(0.34,1.56,0.64,1)}
@keyframes reveal-pop{0%{transform:scale(0) rotate(-10deg);opacity:0}100%{transform:scale(1) rotate(0);opacity:1}}
.case-result-icon{font-size:72px;filter:drop-shadow(0 0 20px currentColor)}
.case-result-name{font-size:20px;font-weight:bold;margin-top:8px}
.case-result-desc{font-size:13px;color:#888;margin-top:4px}
.case-result-stats{display:flex;gap:10px;justify-content:center;margin-top:10px;font-size:13px}
.case-result-btn{margin-top:16px;padding:10px 28px;border-radius:9px;border:none;background:var(--purple);color:#fff;font-size:14px;font-weight:bold;cursor:pointer}
.case-result-btn:hover{background:#7450b0}

/* ═══════════════════════════════════════════════
   RAID ONLINE
═══════════════════════════════════════════════ */
#p-raid{flex-direction:column;gap:10px}
.raid-card{background:var(--card);border-radius:12px;border:1px solid #3d2020;padding:14px}
.raid-card h3{font-size:13px;font-weight:bold;color:#e67e22;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center}
.raid-boss-bar{height:16px;background:#1a1a2e;border-radius:8px;overflow:hidden;margin:8px 0}
.raid-boss-bar-fill{height:16px;background:linear-gradient(90deg,#6b1010,var(--red));border-radius:8px;transition:width .5s}
.raid-party-row{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.pm{background:#0d0d18;border:1px solid var(--border);border-radius:8px;padding:7px 10px;display:flex;flex-direction:column;gap:3px;min-width:100px}
.pm.is-me{border-color:var(--green)}
.pm-name{font-size:12px;font-weight:bold;color:#d4c9a8}
.pm-hp-bar{height:5px;background:#1a1a2e;border-radius:3px;overflow:hidden;margin-top:2px}
.pm-hp-fill{height:5px;border-radius:3px;transition:width .3s}
.pm-hp-fill-me{background:var(--green)}
.pm-hp-fill-ally{background:var(--blue)}
.raid-log{background:#0a0a0f;border:1px solid #1a1a2e;border-radius:8px;padding:8px;max-height:140px;overflow-y:auto;font-size:12px;line-height:1.7}
.raid-log::-webkit-scrollbar{width:3px}
.raid-log::-webkit-scrollbar-thumb{background:#333;border-radius:2px}
.raid-btn{padding:9px 18px;border-radius:8px;border:none;background:#6b1515;color:#ffa0a0;font-size:13px;font-weight:bold;cursor:pointer;border:1px solid #a03030;transition:background .12s}
.raid-btn:hover:not([disabled]){background:#8b2020}
.raid-btn[disabled]{opacity:.4;cursor:not-allowed}
.raid-skill-btn{background:#1e4d7b;color:#80b0ff;border:1px solid #2a5d9b}
.raid-skill-btn:hover:not([disabled]){background:#2980b9}
.raid-open-list{display:flex;flex-direction:column;gap:5px}
.raid-list-row{background:#0d0d18;border:1px solid var(--border);border-radius:8px;padding:9px 12px;display:flex;align-items:center;gap:10px}

/* ═══════════════════════════════════════════════
   CHAT
═══════════════════════════════════════════════ */
#p-chat{flex-direction:column;gap:8px}
#chat-status{font-size:11px;color:#555}
#chat-box{background:var(--card);border-radius:12px;border:1px solid var(--border);height:340px;overflow-y:auto;padding:10px;display:flex;flex-direction:column;gap:5px}
#chat-box::-webkit-scrollbar{width:3px}
#chat-box::-webkit-scrollbar-thumb{background:#333;border-radius:2px}
.cmsg{padding:6px 9px;border-radius:7px;background:#0d0d18;border:1px solid #1a1a2e}
.cmsg.mine{background:rgba(92,61,143,.08);border-color:rgba(92,61,143,.25)}
.cmsg-top{display:flex;align-items:baseline;gap:6px;margin-bottom:2px}
.cmsg-nick{font-size:11px;font-weight:bold;color:var(--purple)}
.cmsg.mine .cmsg-nick{color:var(--gold)}
.cmsg-time{font-size:10px;color:#333}
.cmsg-text{font-size:13px;color:#bbb;word-break:break-word}
#chat-row{display:flex;gap:8px}
#chat-inp{flex:1;padding:9px 12px;border-radius:9px;border:1px solid var(--border);background:var(--card);color:#d4c9a8;font-size:13px;outline:none}
#chat-inp:focus{border-color:var(--purple)}
#chat-sbtn{padding:9px 16px;border-radius:9px;border:none;background:var(--purple);color:#fff;font-size:13px;font-weight:bold;cursor:pointer}
#chat-sbtn:hover{background:#7450b0}

/* FRIENDS */
#p-friends{flex-direction:column;gap:10px}
.fsec{background:var(--card);border-radius:12px;border:1px solid var(--border);padding:14px}
.fsec h3{font-size:11px;color:#555;text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px}
.finp-row{display:flex;gap:8px;margin-bottom:8px}
.finp-row input{flex:1;padding:8px 12px;border-radius:8px;border:1px solid var(--border);background:#0d0d18;color:#d4c9a8;font-size:13px;outline:none}
.finp-row input:focus{border-color:var(--purple)}
.finp-row button{padding:8px 14px;border-radius:8px;border:none;background:var(--purple);color:#fff;font-size:13px;cursor:pointer}
.finp-row button:hover{background:#7450b0}
.friend-row{background:#0d0d18;border:1px solid #1a1a2e;border-radius:8px;padding:8px 12px;display:flex;align-items:center;gap:10px;margin-bottom:5px}
.friend-nick{flex:1;font-size:13px;font-weight:bold;color:#d4c9a8}
.friend-info{font-size:10px;color:#555}
.fbtn2{padding:4px 10px;border-radius:6px;border:1px solid var(--border);background:transparent;color:var(--gold);font-size:11px;cursor:pointer}
.fbtn2:hover{background:rgba(201,162,39,.1);border-color:var(--gold)}
.fbtn2.red{color:#e74c3c}.fbtn2.red:hover{background:rgba(231,76,60,.1);border-color:#e74c3c}
.req-row{background:#0d0d18;border:1px solid rgba(92,61,143,.3);border-radius:8px;padding:8px 12px;display:flex;align-items:center;gap:8px;margin-bottom:5px}
.req-nick{flex:1;font-size:13px;color:#d4c9a8}
.req-btn{padding:4px 10px;border-radius:6px;border:none;font-size:11px;cursor:pointer;font-weight:bold}
.req-btn.acc{background:var(--green);color:#fff}
.req-btn.dec{background:var(--red);color:#fff;margin-left:4px}
.transfer-row{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-top:8px}
.transfer-row select,.transfer-row input{flex:1;min-width:80px;padding:7px 10px;border-radius:8px;border:1px solid var(--border);background:#0d0d18;color:#d4c9a8;font-size:13px;outline:none}
.transfer-row button{padding:7px 14px;border-radius:8px;border:none;background:var(--green);color:#fff;font-size:13px;cursor:pointer;font-weight:bold}

/* LEADERBOARD */
#p-lead{flex-direction:column;gap:6px}
.lrow{background:var(--card);border:1px solid #1a1a2e;border-radius:9px;padding:10px 14px;display:flex;align-items:center;gap:10px}
.lrow.me{border-color:rgba(201,162,39,.4);background:rgba(201,162,39,.04)}
.lpos{font-size:14px;width:28px;text-align:center;color:#555;flex-shrink:0;font-weight:bold}
.lname{flex:1;font-size:13px;font-weight:bold;color:#d4c9a8}
.lscore{font-size:12px;color:var(--gold);font-weight:bold}
.lsub{font-size:10px;color:#555}

/* TOAST */
#toast{position:fixed;bottom:16px;right:16px;background:var(--purple);color:#fff;padding:9px 16px;border-radius:9px;font-size:13px;font-weight:bold;opacity:0;pointer-events:none;transition:opacity .3s,transform .3s;transform:translateY(8px);z-index:9999;max-width:280px}
#toast.on{opacity:1;transform:translateY(0)}

/* ITEM MODAL */
#item-modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.75);display:none;align-items:center;justify-content:center;z-index:300}
#item-modal-bg.on{display:flex}
.imodal{background:#12121e;border:1px solid var(--border);border-radius:14px;padding:20px;max-width:340px;width:90%;max-height:85vh;overflow-y:auto}
.imodal-close{float:right;background:transparent;border:none;color:#555;font-size:18px;cursor:pointer}
.imodal-close:hover{color:#e74c3c}
.imodal-icon{font-size:56px;text-align:center;display:block;margin:6px 0}
.imodal-name{font-size:17px;font-weight:bold;text-align:center;margin-bottom:4px}
.imodal-rarity{text-align:center;margin-bottom:8px}
.imodal-desc{font-size:12px;color:#666;text-align:center;margin-bottom:12px;line-height:1.5}
.imodal-stats{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:14px}
.imodal-stat{background:#0d0d18;border-radius:6px;padding:6px 10px;text-align:center}
.imodal-stat-label{font-size:9px;color:#555;text-transform:uppercase}
.imodal-stat-val{font-size:15px;font-weight:bold;color:#d4c9a8}
.imodal-btns{display:flex;gap:6px}
.imodal-btns button{flex:1;padding:9px;border-radius:8px;border:none;font-size:12px;font-weight:bold;cursor:pointer}
.imbtn-eq{background:var(--green);color:#fff}
.imbtn-eq:hover{background:#2ecc71}
.imbtn-sell{background:#6b1515;color:#ffa0a0;border:1px solid #a03030}
.imbtn-sell:hover{background:#8b2020}
.imbtn-cls{background:#222;color:#aaa}
.imbtn-cls:hover{background:#333}

@media(max-width:620px){
  #p-inv{grid-template-columns:1fr!important}
  .equip-mannequin{grid-template-columns:1fr 50px 1fr}
  .battle-bg{padding:0 20px 15px}
}
</style>
</head>
<body>
<div id="root">

<!-- AUTH -->
<div id="auth-screen">
  <div class="auth-card">
    <div class="auth-logo">⚔</div>
    <div class="auth-title">REALM OF SHADOWS</div>
    <div class="auth-sub">Фэнтезийная RPG — сражайся, прокачивайся, побеждай</div>
    <div class="auth-tabs">
      <button class="atab on" id="atab-in" onclick="amode('in')">Войти</button>
      <button class="atab" id="atab-reg" onclick="amode('reg')">Регистрация</button>
    </div>
    <input class="finp" id="a-login" placeholder="Логин" autocomplete="off">
    <input class="finp" id="a-pass" type="password" placeholder="Пароль" autocomplete="off">
    <div id="a-nick-row" style="display:none"><input class="finp" id="a-nick" placeholder="Имя героя"></div>
    <button class="fbtn" id="auth-btn" onclick="doAuth()">Войти</button>
    <div class="ferr" id="a-err"></div>
  </div>
</div>

<!-- GAME -->
<div id="game" style="display:none">
  <div id="hdr">
    <div class="hdr-l">
      <div id="hdr-name">Герой</div>
      <div class="hdr-bars">
        <div class="hbar-wrap">
          <div class="hbar-label">HP</div>
          <div class="hbar-bg" style="width:110px"><div class="hbar-fill hbar-hp" id="hp-fill" style="width:100%"></div></div>
          <div class="hbar-text" id="hp-text">100/100</div>
        </div>
        <div class="hbar-wrap">
          <div class="hbar-label">XP</div>
          <div class="hbar-bg" style="width:80px"><div class="hbar-fill hbar-xp" id="xp-fill" style="width:0%"></div></div>
          <div class="hbar-text" id="xp-text" style="min-width:40px">0/100</div>
        </div>
      </div>
      <div class="hdr-stats">
        <div class="hstat">Lv.<b id="h-lv">1</b></div>
        <div class="hstat">ATK:<b id="h-atk">10</b></div>
        <div class="hstat">DEF:<b id="h-def">5</b></div>
        <div class="hstat">Gold:<b id="h-gold">0</b></div>
        <div class="hstat" id="h-tp-wrap" style="display:none">TP:<b id="h-tp" style="color:var(--gold)">0</b></div>
      </div>
    </div>
    <div class="hbtns">
      <span id="hdr-user"></span><span class="sdot" id="sdot"></span>
      <button class="hbtn" onclick="saveGame()">Сохранить</button>
      <button class="hbtn red" onclick="doLogout()">Выйти</button>
    </div>
  </div>

  <div id="tabs">
    <button class="tab on"  onclick="goTab('world')">🗺 Мир</button>
    <button class="tab"     onclick="goTab('battle')">⚔ Бой</button>
    <button class="tab"     onclick="goTab('inv')">🎒 Инвентарь</button>
    <button class="tab"     onclick="goTab('talents')">✨ Таланты</button>
    <button class="tab"     onclick="goTab('shop')">🎁 Магазин</button>
    <button class="tab"     onclick="goTab('raid')">🔥 Рейды</button>
    <button class="tab"     onclick="goTab('chat')">💬 Чат</button>
    <button class="tab"     onclick="goTab('friends')">👥 Друзья</button>
    <button class="tab"     onclick="goTab('lead')">🏆 Топ</button>
  </div>

  <!-- WORLD MAP -->
  <div id="p-world" class="panel" style="display:flex">
    <div id="world-map-wrap">
      <svg id="world-svg" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
        <!-- Sky/background -->
        <defs>
          <radialGradient id="sky-grad" cx="50%" cy="30%" r="70%">
            <stop offset="0%" stop-color="#1a0a2e"/>
            <stop offset="100%" stop-color="#080810"/>
          </radialGradient>
          <radialGradient id="glow-forest" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#27ae60" stop-opacity=".5"/>
            <stop offset="100%" stop-color="#27ae60" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="glow-cave" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#3498db" stop-opacity=".4"/>
            <stop offset="100%" stop-color="#3498db" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="glow-ruins" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#e67e22" stop-opacity=".4"/>
            <stop offset="100%" stop-color="#e67e22" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="glow-volcano" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#e74c3c" stop-opacity=".5"/>
            <stop offset="100%" stop-color="#e74c3c" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="glow-abyss" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#9b59b6" stop-opacity=".6"/>
            <stop offset="100%" stop-color="#9b59b6" stop-opacity="0"/>
          </radialGradient>
          <filter id="blur4"><feGaussianBlur stdDeviation="4"/></filter>
          <filter id="blur8"><feGaussianBlur stdDeviation="8"/></filter>
        </defs>
        <!-- Background -->
        <rect width="800" height="400" fill="url(#sky-grad)"/>
        <!-- Stars -->
        <circle cx="50" cy="30" r="1" fill="#fff" opacity=".6"/>
        <circle cx="120" cy="15" r="1.5" fill="#fff" opacity=".5"/>
        <circle cx="200" cy="40" r="1" fill="#fff" opacity=".7"/>
        <circle cx="350" cy="20" r="1" fill="#fff" opacity=".4"/>
        <circle cx="450" cy="35" r="1.5" fill="#fff" opacity=".6"/>
        <circle cx="600" cy="10" r="1" fill="#fff" opacity=".5"/>
        <circle cx="700" cy="25" r="1" fill="#fff" opacity=".8"/>
        <circle cx="750" cy="50" r="1" fill="#fff" opacity=".4"/>
        <circle cx="680" cy="60" r="1.5" fill="#fff" opacity=".3"/>
        <circle cx="80" cy="70" r="1" fill="#fff" opacity=".5"/>
        <!-- Ground -->
        <path d="M0 280 Q200 260 400 270 Q600 280 800 265 L800 400 L0 400 Z" fill="#0d1a0d" opacity=".8"/>
        <path d="M0 300 Q200 285 400 292 Q600 298 800 285 L800 400 L0 400 Z" fill="#0a140a"/>
        <!-- Roads between zones -->
        <path d="M130 300 Q200 280 280 295 Q340 305 420 298 Q500 290 580 300 Q650 308 720 295" stroke="#1a1a1a" stroke-width="6" fill="none" stroke-dasharray="8,4" opacity=".6"/>
        <path d="M130 300 Q200 280 280 295 Q340 305 420 298 Q500 290 580 300 Q650 308 720 295" stroke="#2a2010" stroke-width="3" fill="none" stroke-dasharray="8,4"/>

        <!-- ZONE 1: FOREST -->
        <g class="map-zone-btn" id="mz-forest" onclick="selectZone('forest')" data-zone="forest">
          <ellipse cx="130" cy="295" rx="65" ry="35" fill="url(#glow-forest)" class="zone-glow zone-pulse" filter="url(#blur4)"/>
          <!-- Trees -->
          <polygon points="100,270 115,240 130,270" fill="#0d3d1a" opacity=".9"/>
          <polygon points="115,275 130,245 145,275" fill="#0a4d1a" opacity=".9"/>
          <polygon points="105,280 125,250 145,280" fill="#164d20" opacity=".8"/>
          <rect x="112" y="270" width="6" height="15" fill="#2d1a0a"/>
          <rect x="127" y="275" width="6" height="15" fill="#2d1a0a"/>
          <!-- Zone label -->
          <rect x="78" y="308" width="104" height="22" rx="6" fill="rgba(0,0,0,.7)" stroke="#27ae60" stroke-width="1"/>
          <text x="130" y="323" text-anchor="middle" fill="#27ae60" font-size="11" font-weight="bold" font-family="Arial">🌲 Тёмный Лес</text>
          <text x="130" y="338" text-anchor="middle" fill="#555" font-size="9" font-family="Arial">Уровень 1+</text>
        </g>

        <!-- ZONE 2: CAVE -->
        <g class="map-zone-btn" id="mz-cave" onclick="selectZone('cave')" data-zone="cave">
          <ellipse cx="280" cy="290" rx="65" ry="35" fill="url(#glow-cave)" class="zone-glow" filter="url(#blur4)"/>
          <!-- Mountain/cave -->
          <polygon points="240,290 260,250 280,290" fill="#1a1a2e" opacity=".9"/>
          <polygon points="258,290 278,252 298,290" fill="#1e1e35" opacity=".85"/>
          <polygon points="270,290 290,255 310,290" fill="#15152a" opacity=".9"/>
          <!-- Cave entrance -->
          <ellipse cx="278" cy="288" rx="12" ry="8" fill="#050508"/>
          <rect x="70" y="305" width="104" height="22" rx="6" fill="rgba(0,0,0,.7)" stroke="#3498db" stroke-width="1" transform="translate(144,0)"/>
          <text x="280" y="320" text-anchor="middle" fill="#3498db" font-size="11" font-weight="bold" font-family="Arial">🕳 Пещера Ужаса</text>
          <text x="280" y="335" text-anchor="middle" fill="#555" font-size="9" font-family="Arial">Уровень 3+</text>
        </g>

        <!-- ZONE 3: RUINS -->
        <g class="map-zone-btn" id="mz-ruins" onclick="selectZone('ruins')" data-zone="ruins">
          <ellipse cx="430" cy="285" rx="65" ry="35" fill="url(#glow-ruins)" class="zone-glow" filter="url(#blur4)"/>
          <!-- Ruins columns -->
          <rect x="400" y="260" width="10" height="30" fill="#2a1a0a" opacity=".9"/>
          <rect x="400" y="258" width="14" height="5" fill="#3a2510"/>
          <rect x="420" y="265" width="10" height="25" fill="#2a1a0a" opacity=".9"/>
          <rect x="418" y="263" width="14" height="5" fill="#3a2510"/>
          <rect x="440" y="255" width="10" height="35" fill="#2a1a0a" opacity=".9"/>
          <rect x="438" y="253" width="14" height="5" fill="#3a2510"/>
          <rect x="458" y="268" width="10" height="22" fill="#2a1a0a" opacity=".8"/>
          <!-- floor -->
          <rect x="395" y="288" width="80" height="5" fill="#1a1008" opacity=".7"/>
          <rect x="320" y="302" width="104" height="22" rx="6" fill="rgba(0,0,0,.7)" stroke="#e67e22" stroke-width="1" transform="translate(110,0)"/>
          <text x="430" y="317" text-anchor="middle" fill="#e67e22" font-size="11" font-weight="bold" font-family="Arial">🏛 Древние Руины</text>
          <text x="430" y="332" text-anchor="middle" fill="#555" font-size="9" font-family="Arial">Уровень 7+</text>
        </g>

        <!-- ZONE 4: VOLCANO -->
        <g class="map-zone-btn" id="mz-volcano" onclick="selectZone('volcano')" data-zone="volcano">
          <ellipse cx="590" cy="285" rx="65" ry="35" fill="url(#glow-volcano)" class="zone-glow" filter="url(#blur4)"/>
          <!-- Volcano -->
          <polygon points="548,290 575,235 610,290" fill="#3d1a08" opacity=".95"/>
          <polygon points="560,290 590,238 620,290" fill="#4d2010" opacity=".9"/>
          <!-- Lava glow -->
          <ellipse cx="590" cy="238" rx="12" ry="8" fill="#ff6b1a" opacity=".7" filter="url(#blur4)"/>
          <ellipse cx="590" cy="236" rx="6" ry="4" fill="#ffd166" opacity=".8"/>
          <!-- Lava drips -->
          <path d="M578,255 Q575,268 578,275" stroke="#e67e22" stroke-width="2" fill="none" opacity=".6"/>
          <path d="M600,260 Q603,272 599,280" stroke="#ff6b1a" stroke-width="2" fill="none" opacity=".5"/>
          <rect x="480" y="302" width="104" height="22" rx="6" fill="rgba(0,0,0,.7)" stroke="#e74c3c" stroke-width="1" transform="translate(110,0)"/>
          <text x="590" y="317" text-anchor="middle" fill="#e74c3c" font-size="11" font-weight="bold" font-family="Arial">🌋 Огненная Гора</text>
          <text x="590" y="332" text-anchor="middle" fill="#555" font-size="9" font-family="Arial">Уровень 12+</text>
        </g>

        <!-- ZONE 5: ABYSS -->
        <g class="map-zone-btn" id="mz-abyss" onclick="selectZone('abyss')" data-zone="abyss">
          <ellipse cx="720" cy="290" rx="65" ry="35" fill="url(#glow-abyss)" class="zone-glow" filter="url(#blur4)"/>
          <!-- Abyss portal -->
          <ellipse cx="720" cy="278" rx="28" ry="22" fill="#0d0020" stroke="#5c3d8f" stroke-width="2" opacity=".9"/>
          <ellipse cx="720" cy="278" rx="20" ry="15" fill="#150030" stroke="#9b59b6" stroke-width="1.5" opacity=".8"/>
          <ellipse cx="720" cy="278" rx="10" ry="8" fill="#200040" opacity=".95"/>
          <!-- Portal sparkles -->
          <circle cx="700" cy="265" r="2" fill="#9b59b6" opacity=".7"/>
          <circle cx="740" cy="268" r="2" fill="#7c3ab0" opacity=".6"/>
          <circle cx="710" cy="292" r="1.5" fill="#b060ff" opacity=".8"/>
          <circle cx="730" cy="290" r="2" fill="#9b59b6" opacity=".5"/>
          <rect x="610" y="305" width="104" height="22" rx="6" fill="rgba(0,0,0,.7)" stroke="#9b59b6" stroke-width="1" transform="translate(110,0)"/>
          <text x="720" y="320" text-anchor="middle" fill="#9b59b6" font-size="11" font-weight="bold" font-family="Arial">🌀 Бездна</text>
          <text x="720" y="335" text-anchor="middle" fill="#555" font-size="9" font-family="Arial">Уровень 20+</text>
        </g>

        <!-- Current zone indicator -->
        <g id="map-current-marker" style="display:none">
          <circle r="8" fill="var(--gold)" opacity=".9">
            <animate attributeName="r" values="6;10;6" dur="1.5s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values=".9;.4;.9" dur="1.5s" repeatCount="indefinite"/>
          </circle>
          <text text-anchor="middle" dy="-14" fill="var(--gold)" font-size="10" font-weight="bold" font-family="Arial">ВЫ ЗДЕСЬ</text>
        </g>

        <!-- Lock overlays for zones -->
        <g id="lock-cave" style="display:none">
          <rect x="215" y="240" width="130" height="80" rx="8" fill="rgba(0,0,0,.7)"/>
          <text x="280" y="285" text-anchor="middle" fill="#555" font-size="20" font-family="Arial">🔒</text>
          <text x="280" y="302" text-anchor="middle" fill="#555" font-size="10" font-family="Arial">Ур.3</text>
        </g>
        <g id="lock-ruins" style="display:none">
          <rect x="365" y="240" width="130" height="80" rx="8" fill="rgba(0,0,0,.7)"/>
          <text x="430" y="285" text-anchor="middle" fill="#555" font-size="20" font-family="Arial">🔒</text>
          <text x="430" y="302" text-anchor="middle" fill="#555" font-size="10" font-family="Arial">Ур.7</text>
        </g>
        <g id="lock-volcano" style="display:none">
          <rect x="525" y="235" width="130" height="80" rx="8" fill="rgba(0,0,0,.7)"/>
          <text x="590" y="280" text-anchor="middle" fill="#555" font-size="20" font-family="Arial">🔒</text>
          <text x="590" y="297" text-anchor="middle" fill="#555" font-size="10" font-family="Arial">Ур.12</text>
        </g>
        <g id="lock-abyss" style="display:none">
          <rect x="655" y="240" width="130" height="80" rx="8" fill="rgba(0,0,0,.7)"/>
          <text x="720" y="285" text-anchor="middle" fill="#555" font-size="20" font-family="Arial">🔒</text>
          <text x="720" y="302" text-anchor="middle" fill="#555" font-size="10" font-family="Arial">Ур.20</text>
        </g>
      </svg>
      <div id="map-tooltip"></div>
    </div>
    <!-- Zone info panel below map -->
    <div id="zone-info-panel" style="background:var(--card);border-radius:12px;border:1px solid var(--border);padding:14px;display:flex;align-items:center;gap:14px">
      <div style="font-size:36px" id="zi-icon">🌲</div>
      <div style="flex:1">
        <div style="font-size:15px;font-weight:bold;color:var(--gold)" id="zi-name">Тёмный Лес</div>
        <div style="font-size:12px;color:#666;margin-top:2px" id="zi-desc">Волки, гоблины и разбойники скрываются здесь</div>
        <div style="font-size:11px;color:#555;margin-top:4px" id="zi-enemies">Враги: Волк 🐺, Гоблин 👺, Разбойник 🗡</div>
      </div>
      <button onclick="goToBattle()" id="go-battle-btn" style="padding:10px 20px;border-radius:9px;border:none;background:var(--purple);color:#fff;font-size:13px;font-weight:bold;cursor:pointer;flex-shrink:0">⚔ Сражаться</button>
    </div>
  </div>

  <!-- BATTLE -->
  <div id="p-battle" class="panel">
    <div class="battle-scene" id="battle-scene">
      <div class="battle-idle-msg">Выбери локацию на вкладке <b>Мир</b> и нажми «Сражаться»!</div>
    </div>
  </div>

  <!-- INVENTORY -->
  <div id="p-inv" class="panel" style="grid-template-columns:280px 1fr;gap:10px">
    <div class="inv-left">
      <div class="char-preview">
        <div class="char-avatar" id="char-avatar">⚔</div>
        <div class="char-name" id="char-name-inv">Герой</div>
        <!-- 8-slot mannequin: helmet, weapon, body, armor, ring, pants, gloves, boots, amulet -->
        <div class="equip-mannequin" id="equip-mannequin">
          <!-- Row 1: [empty] [helmet] [empty] -->
          <div></div>
          <div class="eq-slot eq-center" id="eq-helmet" onclick="openEqSlot('helmet')">
            <div class="eq-slot-label">Шлем</div>
            <div class="eq-slot-empty" id="eq-helmet-icon">⛑</div>
            <div class="eq-slot-name" id="eq-helmet-name"></div>
          </div>
          <div></div>
          <!-- Row 2: [weapon] [body/amulet toggle] [armor] -->
          <div class="eq-slot" id="eq-weapon" onclick="openEqSlot('weapon')">
            <div class="eq-slot-label">Оружие</div>
            <div class="eq-slot-empty" id="eq-weapon-icon">⚔</div>
            <div class="eq-slot-name" id="eq-weapon-name"></div>
          </div>
          <div class="eq-slot eq-center" id="eq-amulet" onclick="openEqSlot('amulet')">
            <div class="eq-slot-label">Амулет</div>
            <div class="eq-slot-empty" id="eq-amulet-icon">📿</div>
            <div class="eq-slot-name" id="eq-amulet-name"></div>
          </div>
          <div class="eq-slot" id="eq-armor" onclick="openEqSlot('armor')">
            <div class="eq-slot-label">Броня</div>
            <div class="eq-slot-empty" id="eq-armor-icon">🛡</div>
            <div class="eq-slot-name" id="eq-armor-name"></div>
          </div>
          <!-- Row 3: [gloves] [belt] [ring] -->
          <div class="eq-slot" id="eq-gloves" onclick="openEqSlot('gloves')">
            <div class="eq-slot-label">Перчатки</div>
            <div class="eq-slot-empty" id="eq-gloves-icon">🧤</div>
            <div class="eq-slot-name" id="eq-gloves-name"></div>
          </div>
          <div class="eq-slot eq-center" id="eq-ring" onclick="openEqSlot('ring')">
            <div class="eq-slot-label">Кольцо</div>
            <div class="eq-slot-empty" id="eq-ring-icon">💍</div>
            <div class="eq-slot-name" id="eq-ring-name"></div>
          </div>
          <div class="eq-slot" id="eq-pants" onclick="openEqSlot('pants')">
            <div class="eq-slot-label">Штаны</div>
            <div class="eq-slot-empty" id="eq-pants-icon">👖</div>
            <div class="eq-slot-name" id="eq-pants-name"></div>
          </div>
          <!-- Row 4: [empty] [boots] [empty] -->
          <div></div>
          <div class="eq-slot eq-center" id="eq-boots" onclick="openEqSlot('boots')">
            <div class="eq-slot-label">Сапоги</div>
            <div class="eq-slot-empty" id="eq-boots-icon">👢</div>
            <div class="eq-slot-name" id="eq-boots-name"></div>
          </div>
          <div></div>
        </div>
      </div>
      <div class="stats-mini">
        <h4>Характеристики</h4>
        <div class="stat-row"><span class="stat-row-label">Уровень</span><span class="stat-row-val" id="st-lv">1</span></div>
        <div class="stat-row"><span class="stat-row-label">HP</span><span class="stat-row-val" id="st-hp">100/100</span></div>
        <div class="stat-row"><span class="stat-row-label">Атака (баз+бонус)</span><span class="stat-row-val"><span id="st-base-atk">10</span><span class="bonus" id="st-bonus-atk"></span></span></div>
        <div class="stat-row"><span class="stat-row-label">Защита (баз+бонус)</span><span class="stat-row-val"><span id="st-base-def">5</span><span class="bonus" id="st-bonus-def"></span></span></div>
        <div class="stat-row"><span class="stat-row-label">Крит. шанс</span><span class="stat-row-val" id="st-crit">15%</span></div>
        <div class="stat-row"><span class="stat-row-label">Убийств</span><span class="stat-row-val" id="st-kills">0</span></div>
        <div class="stat-row"><span class="stat-row-label">Золото</span><span class="stat-row-val" style="color:var(--gold)" id="st-gold">0</span></div>
      </div>
    </div>
    <div class="inv-right">
      <h3>Инвентарь <span id="inv-count">0</span> предм. <span id="inv-gold-val" style="color:var(--gold);font-size:12px"></span></h3>
      <div class="inv-sort">
        <button class="sort-btn on" id="sort-rarity" onclick="setSortMode('rarity')">По редкости</button>
        <button class="sort-btn" id="sort-type" onclick="setSortMode('type')">По типу</button>
        <button class="sort-btn" id="sort-new" onclick="setSortMode('new')">Новые</button>
      </div>
      <div class="item-grid" id="inv-grid"></div>
    </div>
  </div>

  <!-- TALENTS -->
  <div id="p-talents" class="panel">
    <div class="talent-header">
      <div>
        <div class="talent-pts" id="talent-pts-big">0</div>
        <div class="talent-pts-label">очков талантов</div>
      </div>
      <div style="flex:1;font-size:12px;color:#666;line-height:1.6">
        Очки талантов получаешь за <b style="color:#d4c9a8">каждый уровень</b>.<br>
        Таланты дают постоянные бонусы к характеристикам.
      </div>
      <div>
        <div style="font-size:12px;color:#666">Следующее ТО на уровне:</div>
        <div style="font-size:15px;font-weight:bold;color:var(--gold)" id="next-talent-lv">—</div>
      </div>
    </div>
    <div class="talent-tree" id="talent-tree"></div>
  </div>

  <!-- SHOP -->
  <div id="p-shop" class="panel">
    <div class="shop-balance">
      <div style="font-size:20px">💰</div>
      <div>
        <div class="shop-gold" id="shop-gold">0</div>
        <div style="font-size:11px;color:#666">золота в кармане</div>
      </div>
    </div>
    <div class="cases-grid" id="cases-grid"></div>
  </div>

  <!-- RAID -->
  <div id="p-raid" class="panel"></div>

  <!-- CHAT -->
  <div id="p-chat" class="panel" style="flex-direction:column;gap:8px">
    <div id="chat-status">Загрузка...</div>
    <div id="chat-box"></div>
    <div id="chat-row">
      <input id="chat-inp" placeholder="Сообщение... (Enter)" onkeydown="if(event.key==='Enter')sendMsg()">
      <button id="chat-sbtn" onclick="sendMsg()">Отправить</button>
    </div>
  </div>

  <!-- FRIENDS -->
  <div id="p-friends" class="panel" style="flex-direction:column;gap:10px">
    <div class="fsec">
      <h3>Входящие заявки</h3>
      <div id="friend-reqs"><div style="color:#444;font-size:13px">Нет заявок</div></div>
    </div>
    <div class="fsec">
      <h3>Добавить друга</h3>
      <div class="finp-row">
        <input id="add-login" placeholder="Логин игрока">
        <button onclick="sendFriendReq()">Добавить</button>
      </div>
    </div>
    <div class="fsec">
      <h3>Мои друзья</h3>
      <div id="friend-list"><div style="color:#444;font-size:13px">Пока нет друзей</div></div>
      <div style="margin-top:12px">
        <div style="font-size:10px;color:#555;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px">Перевести золото другу</div>
        <div class="transfer-row">
          <select id="transfer-to"><option value="">-- выбери друга --</option></select>
          <input id="transfer-amt" type="number" min="1" placeholder="Сколько" style="flex:none;width:110px">
          <button onclick="doTransfer()">Перевести</button>
        </div>
      </div>
    </div>
  </div>

  <!-- LEADERBOARD -->
  <div id="p-lead" class="panel" style="flex-direction:column;gap:6px">
    <div style="font-size:10px;color:#555;text-transform:uppercase;letter-spacing:.06em">Топ героев</div>
    <div id="lead-wrap"><div style="color:#555;padding:20px;text-align:center">Загрузка...</div></div>
  </div>

</div><!-- /game -->
</div><!-- /root -->

<!-- ITEM MODAL -->
<div id="item-modal-bg">
  <div class="imodal">
    <button class="imodal-close" onclick="closeItemModal()">✕</button>
    <div id="imodal-inner"></div>
  </div>
</div>

<!-- CASE OPENING MODAL -->
<div id="case-modal-bg">
  <div id="case-modal-content"></div>
</div>

<div id="toast"></div>

<script>
var API='';
// ═══════════════════════════════════════
// DATA TABLES
// ═══════════════════════════════════════
var ZONES={
  forest: {icon:'🌲',name:'Тёмный Лес',     desc:'Волки, гоблины и разбойники',       reqLv:1,  enemies:['wolf','goblin','bandit'],        bg:'bg-forest', mapX:130, mapY:260},
  cave:   {icon:'🕳',name:'Пещера Ужаса',    desc:'Скелеты, пауки, летучие мыши',      reqLv:3,  enemies:['skeleton','spider','bat'],       bg:'bg-cave',   mapX:280, mapY:260},
  ruins:  {icon:'🏛',name:'Древние Руины',   desc:'Зомби, голем, тёмный маг',          reqLv:7,  enemies:['zombie','golem','darkmage'],     bg:'bg-ruins',  mapX:430, mapY:255},
  volcano:{icon:'🌋',name:'Огненная Гора',   desc:'Огненный элементаль, дракончик',    reqLv:12, enemies:['fire_elem','dragonling','lava_troll'],bg:'bg-volcano',mapX:590,mapY:250},
  abyss:  {icon:'🌀',name:'Бездна',          desc:'Демоны, лич, теневой рыцарь',       reqLv:20, enemies:['demon','lich','shadow_knight'],  bg:'bg-abyss',  mapX:720, mapY:260},
};
var ENEMIES={
  wolf:         {name:'Волк',            icon:'🐺',hp:30, atk:8, def:2, xp:15,gold:[1,5],  pool:'pf_common'},
  goblin:       {name:'Гоблин',          icon:'👺',hp:40, atk:10,def:3, xp:20,gold:[2,8],  pool:'pf_uncommon'},
  bandit:       {name:'Разбойник',       icon:'🗡',hp:55, atk:13,def:4, xp:30,gold:[5,15], pool:'pf_uncommon'},
  skeleton:     {name:'Скелет',          icon:'💀',hp:65, atk:14,def:5, xp:40,gold:[3,12], pool:'pc_common'},
  spider:       {name:'Паук',            icon:'🕷',hp:50, atk:16,def:3, xp:35,gold:[2,8],  pool:'pc_common'},
  bat:          {name:'Летучая мышь',    icon:'🦇',hp:35, atk:12,def:2, xp:25,gold:[1,6],  pool:'pc_common'},
  zombie:       {name:'Зомби',           icon:'🧟',hp:90, atk:18,def:8, xp:60,gold:[8,20], pool:'pr_common'},
  golem:        {name:'Голем',           icon:'🗿',hp:130,atk:22,def:14,xp:90,gold:[12,30],pool:'pr_rare'},
  darkmage:     {name:'Тёмный Маг',      icon:'🧙',hp:80, atk:28,def:6, xp:100,gold:[15,40],pool:'pr_rare'},
  fire_elem:    {name:'Огн. Элем.',      icon:'🔥',hp:150,atk:30,def:10,xp:130,gold:[20,50],pool:'pv_uncommon'},
  dragonling:   {name:'Дракончик',       icon:'🐉',hp:180,atk:35,def:12,xp:180,gold:[30,70],pool:'pv_rare'},
  lava_troll:   {name:'Лавовый Тролль',  icon:'👹',hp:200,atk:28,def:18,xp:160,gold:[25,60],pool:'pv_uncommon'},
  demon:        {name:'Демон',           icon:'😈',hp:250,atk:45,def:15,xp:250,gold:[50,100],pool:'pa_rare'},
  lich:         {name:'Лич',             icon:'☠', hp:220,atk:50,def:10,xp:300,gold:[60,120],pool:'pa_epic'},
  shadow_knight:{name:'Теневой Рыцарь',  icon:'🖤',hp:300,atk:40,def:25,xp:280,gold:[70,150],pool:'pa_epic'},
};
var ITEM_POOLS={
  pf_common:   [{w:40,id:'worn_sword'},{w:35,id:'leather_gloves'},{w:20,id:'iron_ring'},{w:4,id:'hunters_bow'},{w:1,id:'elven_blade'}],
  pf_uncommon: [{w:35,id:'hunters_bow'},{w:25,id:'leather_armor'},{w:20,id:'silver_ring'},{w:12,id:'forest_cloak'},{w:6,id:'elven_blade'},{w:2,id:'druid_amulet'}],
  pc_common:   [{w:40,id:'bone_dagger'},{w:30,id:'iron_helmet'},{w:20,id:'cave_ring'},{w:8,id:'steel_sword'},{w:2,id:'shadow_hood'}],
  pc_rare:     [{w:30,id:'steel_sword'},{w:25,id:'chain_pants'},{w:20,id:'shadow_hood'},{w:15,id:'mana_ring'},{w:8,id:'cursed_blade'},{w:2,id:'battle_gloves'}],
  pr_common:   [{w:35,id:'steel_sword'},{w:30,id:'plate_armor'},{w:20,id:'rune_helmet'},{w:12,id:'cursed_blade'},{w:3,id:'arcane_staff'}],
  pr_rare:     [{w:30,id:'arcane_staff'},{w:25,id:'plate_armor'},{w:20,id:'rune_helmet'},{w:15,id:'guardian_ring'},{w:8,id:'arcane_amulet'},{w:2,id:'soul_crown'}],
  pv_uncommon: [{w:35,id:'dragon_scale'},{w:30,id:'flame_sword'},{w:20,id:'guardian_ring'},{w:12,id:'dragon_helm'},{w:3,id:'phoenix_amulet'}],
  pv_rare:     [{w:35,id:'flame_sword'},{w:25,id:'dragon_helm'},{w:20,id:'volcano_boots'},{w:15,id:'phoenix_amulet'},{w:4,id:'inferno_pants'},{w:1,id:'inferno_blade'}],
  pa_rare:     [{w:35,id:'soul_crown'},{w:30,id:'void_armor'},{w:20,id:'death_ring'},{w:12,id:'shadow_blade'},{w:3,id:'abyss_boots'}],
  pa_epic:     [{w:28,id:'shadow_blade'},{w:22,id:'void_armor'},{w:18,id:'lich_staff'},{w:14,id:'death_ring'},{w:12,id:'abyss_boots'},{w:4,id:'void_amulet'},{w:2,id:'mythic_reaper'}],
};
// CASES
var CASES=[
  {id:'forest_case',   name:'Лесной сундук',   icon:'📦', price:200,  color:'#27ae60', desc:'Снаряжение охотника и лесных духов',
   pools:['pf_common','pf_common','pf_uncommon'], rarities:['common','uncommon','rare']},
  {id:'dungeon_case',  name:'Подземный сундук', icon:'⚰', price:500,  color:'#3498db', desc:'Артефакты пещер и руин',
   pools:['pc_common','pc_rare','pr_common','pr_rare'], rarities:['uncommon','rare','epic']},
  {id:'dragon_case',   name:'Драконий сундук',  icon:'🐲', price:1500, color:'#e67e22', desc:'Сокровища вулкана и драконов',
   pools:['pv_uncommon','pv_rare','pa_rare'], rarities:['rare','epic','legendary']},
  {id:'abyss_case',    name:'Сундук Бездны',    icon:'🌀', price:5000, color:'#9b59b6', desc:'Тёмные артефакты из глубин',
   pools:['pa_rare','pa_epic','pa_epic'], rarities:['epic','legendary','mythic']},
];
// ITEMS — 8 SLOT TYPES
var SLOT_ICONS={weapon:'⚔',armor:'🛡',helmet:'⛑',ring:'💍',gloves:'🧤',pants:'👖',boots:'👢',amulet:'📿'};
var RARITY_LABEL={common:'Обычный',uncommon:'Необычный',rare:'Редкий',epic:'Эпический',legendary:'Легендарный',mythic:'МИФИЧЕСКИЙ'};
var ITEMS={
  // COMMON
  worn_sword:     {n:'Ржавый Меч',          i:'🗡', t:'weapon', r:'common',   atk:3, def:0, hp:0,  crit:0,  desc:'Старый, но острый',           sell:5},
  leather_gloves: {n:'Кожаные Перч.',       i:'🧤', t:'gloves', r:'common',   atk:0, def:2, hp:10, crit:1,  desc:'Простая защита',              sell:4},
  iron_ring:      {n:'Железное Кольцо',     i:'💍', t:'ring',   r:'common',   atk:1, def:1, hp:5,  crit:0,  desc:'Грубая работа',               sell:3},
  bone_dagger:    {n:'Костяной Кинжал',     i:'🦴', t:'weapon', r:'common',   atk:5, def:0, hp:0,  crit:3,  desc:'Сделан из кости монстра',     sell:6},
  iron_helmet:    {n:'Железный Шлем',       i:'⛑', t:'helmet', r:'common',   atk:0, def:3, hp:15, crit:0,  desc:'Надёжная защита',             sell:8},
  cave_ring:      {n:'Пещерное Кольцо',     i:'💍', t:'ring',   r:'common',   atk:2, def:0, hp:8,  crit:2,  desc:'Найдено в пещере',            sell:5},
  // UNCOMMON
  hunters_bow:    {n:'Охотничий Лук',       i:'🏹', t:'weapon', r:'uncommon', atk:8, def:0, hp:0,  crit:5,  desc:'Точный и быстрый',            sell:15},
  leather_armor:  {n:'Кожаная Броня',       i:'🦺', t:'armor',  r:'uncommon', atk:0, def:6, hp:25, crit:0,  desc:'Лёгкая и прочная',            sell:20},
  silver_ring:    {n:'Серебряное Кольцо',   i:'💍', t:'ring',   r:'uncommon', atk:3, def:2, hp:15, crit:2,  desc:'Очищает проклятия',           sell:18},
  steel_sword:    {n:'Стальной Меч',        i:'⚔', t:'weapon', r:'uncommon', atk:12,def:1, hp:0,  crit:4,  desc:'Хорошая сталь',               sell:25},
  chain_pants:    {n:'Кольчужные Штаны',    i:'👖', t:'pants',  r:'uncommon', atk:0, def:7, hp:20, crit:0,  desc:'Звенят при ходьбе',           sell:22},
  shadow_hood:    {n:'Капюшон Теней',       i:'🎭', t:'helmet', r:'uncommon', atk:2, def:4, hp:20, crit:3,  desc:'Растворяешься в тени',        sell:30},
  druid_amulet:   {n:'Амулет Друида',       i:'📿', t:'amulet', r:'uncommon', atk:2, def:2, hp:20, crit:2,  desc:'Связь с природой',            sell:28},
  battle_gloves:  {n:'Боевые Перчатки',     i:'🧤', t:'gloves', r:'uncommon', atk:4, def:3, hp:15, crit:3,  desc:'Усиливают удар',              sell:26},
  // RARE
  elven_blade:    {n:'Эльфийский Клинок',   i:'🌿', t:'weapon', r:'rare',     atk:18,def:2, hp:10, crit:7,  desc:'Выкован из лунного серебра',  sell:80},
  forest_cloak:   {n:'Лесной Плащ',         i:'🍃', t:'armor',  r:'rare',     atk:1, def:12,hp:40, crit:3,  desc:'Шуршит листьями',             sell:70},
  mana_ring:      {n:'Кольцо Маны',         i:'🔮', t:'ring',   r:'rare',     atk:5, def:3, hp:30, crit:4,  desc:'Пульсирует магией',           sell:65},
  cursed_blade:   {n:'Проклятый Клинок',    i:'🖤', t:'weapon', r:'rare',     atk:22,def:0, hp:-10,crit:8,  desc:'Сила требует жертв',          sell:90},
  arcane_staff:   {n:'Арканный Посох',      i:'🪄', t:'weapon', r:'rare',     atk:20,def:3, hp:20, crit:5,  desc:'Усиливает заклинания',        sell:100},
  rune_helmet:    {n:'Рунный Шлем',         i:'⛑', t:'helmet', r:'rare',     atk:3, def:10,hp:40, crit:4,  desc:'Покрыт рунами защиты',        sell:85},
  guardian_ring:  {n:'Кольцо Стража',       i:'💍', t:'ring',   r:'rare',     atk:4, def:6, hp:25, crit:3,  desc:'Защищает от тьмы',            sell:75},
  plate_armor:    {n:'Латные Доспехи',      i:'🛡', t:'armor',  r:'rare',     atk:0, def:18,hp:50, crit:0,  desc:'Тяжёлая броня воина',         sell:110},
  arcane_amulet:  {n:'Аркановый Амулет',    i:'📿', t:'amulet', r:'rare',     atk:6, def:4, hp:35, crit:5,  desc:'Пульсирует тёмной магией',    sell:90},
  battle_pants:   {n:'Латные Штаны',        i:'👖', t:'pants',  r:'rare',     atk:2, def:12,hp:35, crit:2,  desc:'Прочная защита',              sell:80},
  // EPIC
  dragon_scale:   {n:'Чешуя Дракона',       i:'🐉', t:'armor',  r:'epic',     atk:5, def:25,hp:70, crit:4,  desc:'Огненная броня',              sell:300},
  flame_sword:    {n:'Огненный Меч',        i:'🔥', t:'weapon', r:'epic',     atk:35,def:5, hp:15, crit:8,  desc:'Горит вечным пламенем',       sell:350},
  dragon_helm:    {n:'Шлем Дракона',        i:'🐉', t:'helmet', r:'epic',     atk:8, def:18,hp:60, crit:5,  desc:'Дышит огнём',                 sell:280},
  phoenix_amulet: {n:'Амулет Феникса',      i:'📿', t:'amulet', r:'epic',     atk:10,def:8, hp:50, crit:6,  desc:'Возрождает владельца',         sell:320},
  soul_crown:     {n:'Корона Душ',          i:'👑', t:'helmet', r:'epic',     atk:12,def:15,hp:80, crit:6,  desc:'Поглощает души врагов',       sell:400},
  void_armor:     {n:'Броня Пустоты',       i:'🌀', t:'armor',  r:'epic',     atk:8, def:30,hp:60, crit:3,  desc:'Из другого измерения',        sell:450},
  shadow_blade:   {n:'Клинок Теней',        i:'🌑', t:'weapon', r:'epic',     atk:45,def:3, hp:10, crit:10, desc:'Рубит саму тьму',             sell:500},
  death_ring:     {n:'Кольцо Смерти',       i:'💀', t:'ring',   r:'epic',     atk:15,def:10,hp:40, crit:6,  desc:'Холодный как могила',         sell:380},
  lich_staff:     {n:'Посох Лича',          i:'☠', t:'weapon', r:'epic',     atk:50,def:8, hp:-20,crit:9,  desc:'Содержит душу лича',          sell:520},
  volcano_boots:  {n:'Сапоги Вулкана',      i:'👢', t:'boots',  r:'epic',     atk:5, def:14,hp:40, crit:4,  desc:'Оставляют следы огня',        sell:340},
  inferno_pants:  {n:'Штаны Инферно',       i:'👖', t:'pants',  r:'epic',     atk:8, def:18,hp:50, crit:4,  desc:'Горят, но не сгорают',        sell:360},
  void_amulet:    {n:'Амулет Пустоты',      i:'📿', t:'amulet', r:'epic',     atk:12,def:12,hp:60, crit:7,  desc:'Притягивает тёмную энергию',  sell:420},
  abyss_boots:    {n:'Сапоги Бездны',       i:'👢', t:'boots',  r:'epic',     atk:6, def:18,hp:50, crit:5,  desc:'Бесшумны как тьма',           sell:380},
  // LEGENDARY
  inferno_blade:  {n:'Клинок Инферно',      i:'💥', t:'weapon', r:'legendary',atk:60,def:10,hp:20, crit:12, desc:'Испепеляет всё живое',        sell:1500},
  legend_bow:     {n:'Лук Легенды',         i:'🏹', t:'weapon', r:'legendary',atk:55,def:5, hp:30, crit:15, desc:'Стрелы никогда не промахуются',sell:1400},
  nature_ring:    {n:'Кольцо Природы',      i:'🌿', t:'ring',   r:'legendary',atk:20,def:20,hp:100,crit:8,  desc:'Гармония всего живого',       sell:1800},
  druid_staff:    {n:'Посох Друида',        i:'🌳', t:'weapon', r:'legendary',atk:48,def:15,hp:60, crit:10, desc:'Голос леса',                  sell:1600},
  legend_boots:   {n:'Сапоги Легенды',      i:'👢', t:'boots',  r:'legendary',atk:12,def:25,hp:80, crit:8,  desc:'Быстрее ветра',               sell:1650},
  legend_pants:   {n:'Латы Паладина',       i:'👖', t:'pants',  r:'legendary',atk:10,def:28,hp:90, crit:6,  desc:'Носил великий паладин',       sell:1700},
  legend_gloves:  {n:'Перчатки Титана',     i:'🧤', t:'gloves', r:'legendary',atk:18,def:15,hp:60, crit:10, desc:'Сила великанов',              sell:1750},
  legend_amulet:  {n:'Амулет Вечности',     i:'📿', t:'amulet', r:'legendary',atk:15,def:20,hp:100,crit:9,  desc:'Дарует бессмертие духу',      sell:1900},
  // MYTHIC
  mythic_reaper:  {n:'Жнец Бездны [МИФ]',  i:'👿', t:'weapon', r:'mythic',   atk:100,def:25,hp:-30,crit:20,desc:'Абсолютная тьма',             sell:8000},
  mythic_armor:   {n:'Доспех Богов [МИФ]',  i:'⚡', t:'armor',  r:'mythic',   atk:20,def:60,hp:200,crit:8,  desc:'Непробиваемый',               sell:9000},
  mythic_helm:    {n:'Корона Тьмы [МИФ]',   i:'👑', t:'helmet', r:'mythic',   atk:25,def:45,hp:150,crit:15, desc:'Правитель нечисти',           sell:7500},
};
// TALENTS
var TALENT_DEFS=[
  {id:'berserker',   branch:'Воин',    icon:'⚔',  name:'Берсерк',      desc:'ATK +5 на уровень',      maxLv:5, costPer:1, effect:'atk', per:5},
  {id:'iron_skin',   branch:'Воин',    icon:'🛡', name:'Железная кожа',desc:'DEF +4 на уровень',      maxLv:5, costPer:1, effect:'def', per:4},
  {id:'vital_force', branch:'Воин',    icon:'❤',  name:'Жизненная сила',desc:'MaxHP +30 на уровень',  maxLv:5, costPer:1, effect:'hp',  per:30},
  {id:'critical',    branch:'Разведчик',icon:'🎯',name:'Точный удар',   desc:'Крит +3% на уровень',   maxLv:5, costPer:1, effect:'crit',per:3},
  {id:'dodge',       branch:'Разведчик',icon:'💨',name:'Уклонение',     desc:'Шанс уклона +4%',       maxLv:3, costPer:1, effect:'dodge',per:4},
  {id:'treasure',    branch:'Разведчик',icon:'💰',name:'Знаток сокровищ',desc:'+20% к золоту с врагов',maxLv:3, costPer:1, effect:'gold', per:20},
  {id:'arcane_pow',  branch:'Маг',     icon:'🔮',name:'Арканная мощь',  desc:'ATK +8 (только маг)',   maxLv:3, costPer:2, effect:'atk', per:8},
  {id:'mana_shield', branch:'Маг',     icon:'✨',name:'Щит Маны',       desc:'DEF +6 на уровень',     maxLv:4, costPer:2, effect:'def', per:6},
  {id:'double_cast', branch:'Маг',     icon:'⚡',name:'Двойное Заклин.',desc:'Шанс 2 удара подряд +5%',maxLv:3,costPer:2, effect:'dblcast',per:5},
];
// ═══════════════════════════════════════
// PLAYER STATE
// ═══════════════════════════════════════
var P={
  hp:100,maxHp:100,atk:10,def:5,crit:15,dodge:0,
  gold:0,level:1,xp:0,kills:0,totalKills:0,
  zone:'forest',
  inventory:[],
  equipped:{weapon:null,armor:null,helmet:null,ring:null,gloves:null,pants:null,boots:null,amulet:null},
  talents:{},      // {talentId: level}
  talentPoints:0,
  invSortMode:'rarity',
};
var curUser=null,curTab='world',loopsOn=false;
var currentZone='forest';
var invAddOrder=[];  // track add order for 'new' sort

// ═══════════════════════════════════════
// UTILS
// ═══════════════════════════════════════
function fmt(n){n=Math.floor(n);if(n>=1e6)return(n/1e6).toFixed(1)+'M';if(n>=1e3)return(n/1e3).toFixed(1)+'K';return String(n);}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function rnd(a,b){return Math.floor(Math.random()*(b-a+1))+a;}
function pick(arr){return arr[Math.floor(Math.random()*arr.length)];}
var toastT=null;
function toast(m,c){var t=document.getElementById('toast');t.textContent=m;t.style.background=c||'#5c3d8f';t.className='on';clearTimeout(toastT);toastT=setTimeout(function(){t.className='';},2800);}
function flashDot(){var d=document.getElementById('sdot');d.className='sdot on';setTimeout(function(){d.className='sdot';},1500);}
async function api(path,body){var opts={headers:{'Content-Type':'application/json'}};if(body){opts.method='POST';opts.body=JSON.stringify(body);}var r=await fetch(API+path,opts);var j=await r.json();if(!r.ok)throw new Error(j.detail||'Ошибка сервера');return j;}

// ═══════════════════════════════════════
// AUTH
// ═══════════════════════════════════════
var authIsReg=false;
function amode(m){authIsReg=m==='reg';document.getElementById('atab-in').className='atab'+(m==='in'?' on':'');document.getElementById('atab-reg').className='atab'+(m==='reg'?' on':'');document.getElementById('auth-btn').textContent=m==='in'?'Войти':'Создать героя';document.getElementById('a-nick-row').style.display=m==='reg'?'block':'none';document.getElementById('a-err').textContent='';}
async function doAuth(){
  var login=document.getElementById('a-login').value.trim().toLowerCase();
  var pass=document.getElementById('a-pass').value;
  var err=document.getElementById('a-err'),btn=document.getElementById('auth-btn');
  err.textContent='';
  if(!login||login.length<3){err.textContent='Логин: мин. 3 символа';return;}
  if(!pass||pass.length<3){err.textContent='Пароль: мин. 3 символа';return;}
  btn.disabled=true;btn.textContent='Загрузка...';
  try{
    var data;
    if(authIsReg){var nick=document.getElementById('a-nick').value.trim();if(!nick||nick.length<2){err.textContent='Имя: мин. 2 символа';return;}data=await api('/api/register',{login:login,password:pass,nick:nick});}
    else{data=await api('/api/login',{login:login,password:pass});}
    curUser={login:data.login,nick:data.nick,passhash:data.passhash};
    if(data.game_data&&Object.keys(data.game_data).length)loadGD(data.game_data);
    recalcStats();startGame();
  }catch(e){err.textContent=e.message;}
  finally{btn.disabled=false;btn.textContent=authIsReg?'Создать героя':'Войти';}
}
function loadGD(d){
  var keys=['hp','maxHp','gold','level','xp','kills','totalKills','crit','dodge','talentPoints'];
  keys.forEach(function(k){if(d[k]!==undefined)P[k]=Number(d[k])||0;});
  if(d.zone)currentZone=P.zone=d.zone;
  if(d.inventory)P.inventory=d.inventory;
  if(d.equipped)P.equipped=Object.assign({weapon:null,armor:null,helmet:null,ring:null,gloves:null,pants:null,boots:null,amulet:null},d.equipped);
  if(d.talents)P.talents=d.talents;
  if(d.invOrder)invAddOrder=d.invOrder;
}
function getGD(){
  return{hp:P.hp,maxHp:P.maxHp,gold:P.gold,level:P.level,xp:P.xp,kills:P.kills,totalKills:P.totalKills,
    crit:P.crit,dodge:P.dodge,talentPoints:P.talentPoints,zone:currentZone,
    inventory:P.inventory,equipped:P.equipped,talents:P.talents,invOrder:invAddOrder};
}
async function saveGame(manual){if(!curUser)return;try{await api('/api/save',{login:curUser.login,passhash:curUser.passhash,game_data:getGD()});flashDot();if(manual)toast('Сохранено!','#27ae60');}catch(e){if(manual)toast('Ошибка','#e74c3c');}}
function doLogout(){saveGame(false);curUser=null;battle.active=false;document.getElementById('game').style.display='none';document.getElementById('auth-screen').style.display='flex';document.getElementById('a-pass').value='';}

// ═══════════════════════════════════════
// STATS
// ═══════════════════════════════════════
function recalcStats(){
  var baseAtk=10+Math.floor((P.level-1)*2.5);
  var baseDef=5+Math.floor((P.level-1)*1.5);
  var baseHp=100+Math.floor((P.level-1)*20);
  var baseCrit=15;
  var bonusAtk=0,bonusDef=0,bonusHp=0,bonusCrit=0,bonusDodge=0;
  // Equipped items
  for(var slot in P.equipped){var id=P.equipped[slot];if(id&&ITEMS[id]){bonusAtk+=ITEMS[id].atk||0;bonusDef+=ITEMS[id].def||0;bonusHp+=ITEMS[id].hp||0;bonusCrit+=ITEMS[id].crit||0;}}
  // Talents
  for(var tid in P.talents){
    var lv=P.talents[tid]||0;
    var td=TALENT_DEFS.find(function(t){return t.id===tid;});
    if(!td||!lv)continue;
    var bonus=lv*td.per;
    if(td.effect==='atk')bonusAtk+=bonus;
    else if(td.effect==='def')bonusDef+=bonus;
    else if(td.effect==='hp')bonusHp+=bonus;
    else if(td.effect==='crit')bonusCrit+=bonus;
    else if(td.effect==='dodge')bonusDodge+=bonus;
  }
  P.atk=baseAtk+bonusAtk;
  P.def=baseDef+bonusDef;
  P.maxHp=Math.max(50,baseHp+bonusHp);
  P.crit=Math.min(60,baseCrit+bonusCrit);
  P.dodge=Math.min(40,bonusDodge);
  P.baseAtk=baseAtk; P.baseDef=baseDef; P.bonusAtk=bonusAtk; P.bonusDef=bonusDef;
  if(P.hp>P.maxHp)P.hp=P.maxHp;
}
function xpNeeded(){return Math.floor(100*Math.pow(1.4,P.level-1));}
function gainXP(amount){
  P.xp+=amount;
  var needed=xpNeeded();
  if(P.xp>=needed){
    P.xp-=needed;P.level++;P.talentPoints++;
    recalcStats();P.hp=P.maxHp;
    toast('Уровень '+P.level+'! +1 очко таланта','#c9a227');
    if(curTab==='inv')updateInvStats();
  }
  updateHdr();
}
function getGoldMult(){
  var mult=1;
  var t=P.talents['treasure']||0;
  if(t)mult+=t*0.2;
  return mult;
}

// ═══════════════════════════════════════
// HEADER
// ═══════════════════════════════════════
function updateHdr(){
  document.getElementById('hp-fill').style.width=Math.max(0,Math.round(P.hp/P.maxHp*100))+'%';
  document.getElementById('hp-text').textContent=Math.ceil(P.hp)+'/'+P.maxHp;
  var xpN=xpNeeded();
  document.getElementById('xp-fill').style.width=Math.min(100,Math.round(P.xp/xpN*100))+'%';
  document.getElementById('xp-text').textContent=P.xp+'/'+xpN;
  document.getElementById('h-lv').textContent=P.level;
  document.getElementById('h-atk').textContent=P.atk;
  document.getElementById('h-def').textContent=P.def;
  document.getElementById('h-gold').textContent=fmt(P.gold);
  var tp=P.talentPoints||0;
  document.getElementById('h-tp-wrap').style.display=tp>0?'':'none';
  document.getElementById('h-tp').textContent=tp;
}

// ═══════════════════════════════════════
// START GAME
// ═══════════════════════════════════════
function startGame(){
  document.getElementById('auth-screen').style.display='none';
  document.getElementById('game').style.display='block';
  document.getElementById('hdr-user').textContent=curUser.nick;
  document.getElementById('char-name-inv').textContent=curUser.nick;
  updateHdr();updateMapUI();buildTalentTree();buildShop();buildRaids();
  goTab('world');
  if(!loopsOn){loopsOn=true;setInterval(function(){if(curUser)saveGame(false);},25000);setInterval(function(){if(curTab==='chat')loadChat();if(curTab==='friends')loadFriends();if(activeRaidId&&curTab==='raid')pollRaid();},3500);}
}

// ═══════════════════════════════════════
// TABS
// ═══════════════════════════════════════
function goTab(name){
  curTab=name;
  var names=['world','battle','inv','talents','shop','raid','chat','friends','lead'];
  document.querySelectorAll('.tab').forEach(function(t,i){t.className='tab'+(names[i]===name?' on':'');});
  document.querySelectorAll('.panel').forEach(function(p){p.style.display='none';});
  var el=document.getElementById('p-'+name);if(!el)return;
  if(name==='world'||name==='battle'||name==='chat'||name==='friends'||name==='lead'||name==='shop'||name==='raid'||name==='talents')el.style.display='flex';
  else if(name==='inv')el.style.display='grid';
  if(name==='world')updateMapUI();
  if(name==='inv'){updateEquipSlots();updateInvGrid();updateInvStats();}
  if(name==='talents')updateTalentTree();
  if(name==='shop'){document.getElementById('shop-gold').textContent=fmt(P.gold);}
  if(name==='chat')loadChat();
  if(name==='friends')loadFriends();
  if(name==='lead')loadLead();
  if(name==='raid')buildRaids();
}

// ═══════════════════════════════════════
// WORLD MAP
// ═══════════════════════════════════════
function updateMapUI(){
  // Lock overlays
  var locks={cave:3,ruins:7,volcano:12,abyss:20};
  for(var zid in locks){
    var lock=document.getElementById('lock-'+zid);
    if(lock)lock.style.display=P.level<locks[zid]?'block':'none';
  }
  // Marker
  var marker=document.getElementById('map-current-marker');
  var z=ZONES[currentZone];
  if(marker&&z){
    marker.style.display='block';
    marker.setAttribute('transform','translate('+z.mapX+','+(z.mapY-20)+')');
  }
  // Zone info panel
  if(z){
    document.getElementById('zi-icon').textContent=z.icon;
    document.getElementById('zi-name').textContent=z.name;
    document.getElementById('zi-desc').textContent=z.desc;
    var enames=z.enemies.map(function(eid){var e=ENEMIES[eid];return e?e.name+' '+e.icon:'';}).join(', ');
    document.getElementById('zi-enemies').textContent='Враги: '+enames;
  }
  // Setup zone hover tooltips & click handlers
  Object.keys(ZONES).forEach(function(zid){
    var el=document.getElementById('mz-'+zid);
    if(!el)return;
    var locked=P.level<ZONES[zid].reqLv;
    el.style.cursor=locked?'not-allowed':'pointer';
    el.onmouseenter=function(e){
      if(locked)return;
      var tip=document.getElementById('map-tooltip');
      var z2=ZONES[zid];
      tip.innerHTML='<b>'+z2.icon+' '+esc(z2.name)+'</b>'+z2.desc+'<br><span style="color:#555;font-size:10px">Нажми чтобы перейти</span>';
      tip.style.display='block';
      var svg=document.getElementById('world-map-wrap');
      var rect=svg.getBoundingClientRect();
      tip.style.left=Math.min(e.clientX-rect.left+10,rect.width-170)+'px';
      tip.style.top=(e.clientY-rect.top+10)+'px';
    };
    el.onmouseleave=function(){document.getElementById('map-tooltip').style.display='none';};
  });
}

function selectZone(zid){
  var z=ZONES[zid];if(!z)return;
  if(P.level<z.reqLv){toast('Нужен уровень '+z.reqLv,'#e74c3c');return;}
  currentZone=zid;P.zone=zid;
  updateMapUI();
  document.getElementById('map-tooltip').style.display='none';
  var zi=document.getElementById('zi-icon'),zn=document.getElementById('zi-name'),zd=document.getElementById('zi-desc'),ze=document.getElementById('zi-enemies');
  if(zi){zi.textContent=z.icon;zn.textContent=z.name;zd.textContent=z.desc;
    var enames=z.enemies.map(function(eid){var e=ENEMIES[eid];return e?e.name+' '+e.icon:'';}).join(', ');
    ze.textContent='Враги: '+enames;}
}

function goToBattle(){
  startBattle(currentZone);
  goTab('battle');
}

// ═══════════════════════════════════════
// BATTLE ENGINE
// ═══════════════════════════════════════
var battle={active:false,enemy:null,enemyHp:0,enemyMaxHp:0,zone:null,log:[],skillCd:0,healCd:0};
var skillCdTimer=null;

function getEnemy(zoneId){
  var z=ZONES[zoneId||currentZone];
  if(!z)return Object.assign({id:'wolf'},ENEMIES.wolf);
  var eid=pick(z.enemies);
  return Object.assign({id:eid},ENEMIES[eid]);
}

function startBattle(zoneId){
  if(P.hp<=0){restoreHP();return;}
  var z=ZONES[zoneId];
  if(!z||P.level<z.reqLv){toast('Нужен уровень '+z.reqLv,'#e74c3c');return;}
  var eBase=getEnemy(zoneId);
  var lvB=Math.max(0,P.level-1);
  var scaledHp=Math.floor(eBase.hp*(1+lvB*0.12));
  battle={
    active:true,zone:zoneId,enemy:eBase,
    enemyHp:scaledHp,enemyMaxHp:scaledHp,
    log:[],skillCd:0,healCd:0
  };
  renderBattle();
  blogAdd('sys','--- '+eBase.name+' '+eBase.icon+' появился! ---');
}

function renderBattle(){
  var scene=document.getElementById('battle-scene');
  if(!battle.active){
    scene.innerHTML='<div class="battle-idle-msg">Выбери локацию на вкладке <b>Мир</b> и нажми «Сражаться»!</div>';
    return;
  }
  var e=battle.enemy;
  var z=ZONES[battle.zone]||{bg:'bg-forest'};
  var php=Math.max(0,Math.ceil(P.hp)),ehp=Math.max(0,Math.ceil(battle.enemyHp));
  var ppct=Math.max(0,Math.round(P.hp/P.maxHp*100)),epct=Math.max(0,Math.round(battle.enemyHp/battle.enemyMaxHp*100));
  var skillReady=battle.skillCd<=0,healReady=battle.healCd<=0;

  scene.innerHTML=
    '<div class="battle-bg '+z.bg+'" id="battle-bg">'
    // BG decorations
    +'<div style="position:absolute;inset:0;overflow:hidden;pointer-events:none" id="battle-deco-layer"></div>'
    // Player
    +'<div class="player-sprite" id="player-sprite">'
    +'<div class="sprite-body" id="player-body">⚔</div>'
    +'<div class="sprite-name">'+esc(curUser.nick)+'</div>'
    +'</div>'
    // Enemy
    +'<div class="enemy-sprite" id="enemy-sprite">'
    +'<div class="enemy-body" id="enemy-body">'+e.icon+'</div>'
    +'<div class="sprite-name r-common">'+esc(e.name)+'</div>'
    +'</div>'
    +'</div>'
    // HP bars
    +'<div class="battle-hpbars">'
    +'<div class="bhp-block">'
    +'<div class="bhp-name">'+esc(curUser.nick)+'</div>'
    +'<div class="bhp-bar-bg" style="width:100%"><div class="bhp-bar bhp-p" id="bhp-player" style="width:'+ppct+'%"></div></div>'
    +'<div class="bhp-val" id="bhp-player-txt">'+php+'/'+P.maxHp+'</div>'
    +'</div>'
    +'<div class="vs-badge">VS</div>'
    +'<div class="bhp-block enemy-side">'
    +'<div class="bhp-name">'+esc(e.name)+'</div>'
    +'<div class="bhp-bar-bg" style="width:100%"><div class="bhp-bar bhp-e" id="bhp-enemy" style="width:'+epct+'%"></div></div>'
    +'<div class="bhp-val" id="bhp-enemy-txt">'+ehp+'/'+battle.enemyMaxHp+'</div>'
    +'</div>'
    +'</div>'
    // Log
    +'<div class="battle-log-wrap" id="battle-log"></div>'
    // Actions
    +'<div class="battle-actions">'
    +'<button class="bact bact-atk" id="btn-atk" onclick="doAttack()">⚔ Атака</button>'
    +'<button class="bact bact-skill" id="btn-skill" onclick="doSkill()"'+(skillReady?'':' disabled')+'>🔥 Навык<span class="skill-cd" id="skill-cd-txt">'+(skillReady?'':battle.skillCd+'с')+'</span></button>'
    +'<button class="bact bact-heal" id="btn-heal" onclick="doHeal()"'+(healReady?'':' disabled')+'>💚 Лечение<span class="skill-cd" id="heal-cd-txt">'+(healReady?'':battle.healCd+'с')+'</span></button>'
    +'<button class="bact bact-flee" onclick="doFlee()">🏃 Бежать</button>'
    +'</div>';

  // Repopulate log
  var logEl=document.getElementById('battle-log');
  battle.log.forEach(function(l){var d=document.createElement('div');d.className='blog '+l.t;d.textContent=l.msg;logEl.appendChild(d);});
  logEl.scrollTop=logEl.scrollHeight;
  addBgDeco(battle.zone);
}

function addBgDeco(zid){
  var layer=document.getElementById('battle-deco-layer');if(!layer)return;
  var decos={
    forest:'<text x="10%" y="80%" font-size="28" opacity=".4" style="pointer-events:none">🌲</text><text x="20%" y="70%" font-size="20" opacity=".3">🌳</text><text x="75%" y="75%" font-size="24" opacity=".4">🌲</text><text x="85%" y="65%" font-size="18" opacity=".3">🍃</text>',
    cave:  '<text x="5%"  y="75%" font-size="22" opacity=".3">🦇</text><text x="80%" y="70%" font-size="18" opacity=".3">💎</text><text x="15%" y="60%" font-size="14" opacity=".4">🪨</text><text x="72%" y="55%" font-size="14" opacity=".3">🪨</text>',
    ruins: '<text x="5%"  y="70%" font-size="22" opacity=".3">🏛</text><text x="78%" y="68%" font-size="20" opacity=".3">⚱</text><text x="15%" y="55%" font-size="14" opacity=".4">🗿</text>',
    volcano:'<text x="5%" y="65%" font-size="22" opacity=".4">🌋</text><text x="78%" y="62%" font-size="18" opacity=".4">🔥</text><text x="42%" y="25%" font-size="14" opacity=".6">💨</text>',
    abyss: '<text x="8%"  y="60%" font-size="22" opacity=".4">🌀</text><text x="76%" y="58%" font-size="18" opacity=".4">👁</text><text x="45%" y="20%" font-size="14" opacity=".5">✨</text>',
  };
  layer.innerHTML=decos[zid]||'';
}

function blogAdd(type,msg){
  battle.log.push({t:type,msg:msg});
  if(battle.log.length>40)battle.log.shift();
  var el=document.getElementById('battle-log');if(!el)return;
  var d=document.createElement('div');d.className='blog '+type;d.textContent=msg;
  el.appendChild(d);el.scrollTop=el.scrollHeight;
}

function spawnDmgFloat(dmg,isCrit,isHeal,isEnemy){
  var scene=document.getElementById('battle-bg');if(!scene)return;
  var d=document.createElement('div');
  d.className='dmg-float '+(isHeal?'dmg-heal':isCrit?'dmg-crit':(isEnemy?'dmg-enemy':'dmg-player'));
  d.textContent=(isHeal?'+':'-')+fmt(dmg)+(isCrit?'!':'');
  d.style.left=(isEnemy?'60':'25')+'%';
  d.style.top='60px';
  scene.style.position='relative';
  scene.appendChild(d);
  setTimeout(function(){if(d.parentNode)d.parentNode.removeChild(d);},900);
}

function animSprite(id,cls){
  var el=document.getElementById(id);if(!el)return;
  el.classList.add(cls);
  setTimeout(function(){el.classList.remove(cls);},450);
}

function updateBattleBars(){
  var php=Math.max(0,Math.ceil(P.hp)),ehp=Math.max(0,Math.ceil(battle.enemyHp));
  var ppct=Math.max(0,Math.round(P.hp/P.maxHp*100)),epct=Math.max(0,Math.round(battle.enemyHp/battle.enemyMaxHp*100));
  var bpp=document.getElementById('bhp-player');if(bpp)bpp.style.width=ppct+'%';
  var bep=document.getElementById('bhp-enemy');if(bep)bep.style.width=epct+'%';
  var bpt=document.getElementById('bhp-player-txt');if(bpt)bpt.textContent=php+'/'+P.maxHp;
  var bet=document.getElementById('bhp-enemy-txt');if(bet)bet.textContent=ehp+'/'+battle.enemyMaxHp;
  updateHdr();
}

function disableActions(dis){
  ['btn-atk','btn-skill','btn-heal'].forEach(function(id){var b=document.getElementById(id);if(b)b.disabled=dis;});
}

function calcDmg(atk,def){
  var base=Math.max(1,atk-Math.floor(def*0.55));
  var crit=Math.random()*100<P.crit;
  var dmg=Math.floor(base*(0.8+Math.random()*0.4)*(crit?1.9:1));
  return{dmg:dmg,crit:crit};
}
function calcDodge(){return Math.random()*100<(P.dodge||0);}

function doAttack(){
  if(!battle.active)return;disableActions(true);
  var res=calcDmg(P.atk,battle.enemy.def);
  battle.enemyHp-=res.dmg;
  animSprite('player-body','attack-anim');
  setTimeout(function(){animSprite('enemy-body','hurt-anim');spawnDmgFloat(res.dmg,res.crit,false,true);},250);
  if(res.crit)blogAdd('crit','КРИТ! Ты наносишь '+res.dmg+' урона '+battle.enemy.name+'!');
  else blogAdd('atk','Ты атакуешь '+battle.enemy.name+' — '+res.dmg+' урона.');
  updateBattleBars();
  if(battle.enemyHp<=0){endBattle(true);return;}
  setTimeout(function(){enemyTurn();},600);
}

function doSkill(){
  if(!battle.active||battle.skillCd>0)return;disableActions(true);
  var skillAtk=Math.floor(P.atk*1.7);
  var doubleCast=(P.talents['double_cast']||0)*5;
  var hits=1+(Math.random()*100<doubleCast?1:0);
  var totalDmg=0;
  for(var i=0;i<hits;i++){var res=calcDmg(skillAtk,battle.enemy.def);totalDmg+=res.dmg;battle.enemyHp-=res.dmg;}
  battle.skillCd=6;
  animSprite('player-body','attack-anim');
  setTimeout(function(){animSprite('enemy-body','hurt-anim');spawnDmgFloat(totalDmg,true,false,true);},250);
  blogAdd('crit','Мощный удар'+(hits>1?' x'+hits:'')+'! '+totalDmg+' урона!');
  updateBattleBars();
  startCdTimer('skill',6,'skill-cd-txt','btn-skill');
  if(battle.enemyHp<=0){endBattle(true);return;}
  setTimeout(function(){enemyTurn();},600);
}

function doHeal(){
  if(!battle.active||battle.healCd>0)return;disableActions(true);
  var heal=Math.floor(P.maxHp*0.25);
  P.hp=Math.min(P.maxHp,P.hp+heal);
  battle.healCd=10;
  spawnDmgFloat(heal,false,true,false);
  blogAdd('heal','Ты использовал лечение! +'+heal+' HP.');
  updateBattleBars();
  startCdTimer('heal',10,'heal-cd-txt','btn-heal');
  setTimeout(function(){enemyTurn();},400);
}

function startCdTimer(type,secs,txtId,btnId){
  var left=secs;
  var t=setInterval(function(){
    left--;
    if(type==='skill')battle.skillCd=left;
    else battle.healCd=left;
    var txt=document.getElementById(txtId);if(txt)txt.textContent=left>0?left+'с':'';
    var btn=document.getElementById(btnId);if(btn&&battle.active)btn.disabled=left>0;
    if(left<=0)clearInterval(t);
  },1000);
}

function doFlee(){
  if(!battle.active)return;
  if(Math.random()<0.45){blogAdd('sys','Ты сбежал!');battle.active=false;setTimeout(renderBattle,400);}
  else{blogAdd('sys','Не удалось сбежать!');disableActions(true);setTimeout(enemyTurn,400);}
}

function enemyTurn(){
  if(!battle.active)return;
  // Dodge check
  if(calcDodge()){
    blogAdd('sys','Ты уклонился от удара!');
    updateBattleBars();disableActions(false);return;
  }
  var res=calcDmg(battle.enemy.atk,P.def);
  P.hp-=res.dmg;if(P.hp<0)P.hp=0;
  animSprite('enemy-body','attack-anim');
  setTimeout(function(){animSprite('player-body','hurt-anim');spawnDmgFloat(res.dmg,res.crit,false,false);},250);
  if(res.crit)blogAdd('crit',battle.enemy.name+' КРИТ! -'+res.dmg+' HP тебе!');
  else blogAdd('def',battle.enemy.name+' атакует — -'+res.dmg+' HP.');
  updateBattleBars();
  if(P.hp<=0){endBattle(false);return;}
  disableActions(false);
}

function endBattle(won){
  disableActions(true);
  if(won){
    var e=battle.enemy;
    var goldGain=Math.floor(rnd(e.gold[0],e.gold[1])*getGoldMult());
    P.gold+=goldGain;P.kills++;P.totalKills++;
    blogAdd('loot','Победа! +'+goldGain+' золота.');
    gainXP(e.xp);
    var loot=tryDrop(e.pool);
    if(loot){
      var uid=Date.now()+'_'+Math.random().toString(36).slice(2,7);
      P.inventory.push({id:loot,uid:uid,ts:Date.now()});
      invAddOrder.push(uid);
      var item=ITEMS[loot];
      blogAdd('loot','Выбил: '+item.n+' ['+RARITY_LABEL[item.r]+']!');
      toast(item.i+' '+item.n+' ['+RARITY_LABEL[item.r]+']!','#c9a227');
    }
    updateHdr();battle.active=false;
    setTimeout(function(){startBattle(battle.zone);},900);
  } else {
    blogAdd('die','Ты погиб! Восстановлено 30% HP.');
    battle.active=false;P.hp=Math.floor(P.maxHp*0.3);
    updateHdr();disableActions(false);
    setTimeout(renderBattle,700);
  }
}
function restoreHP(){P.hp=Math.floor(P.maxHp*0.5);updateHdr();}

function tryDrop(pool){
  var p=ITEM_POOLS[pool];if(!p)return null;
  if(Math.random()>0.38)return null;
  var tot=p.reduce(function(s,x){return s+x.w;},0);
  var roll=Math.random()*tot,acc=0;
  for(var i=0;i<p.length;i++){acc+=p[i].w;if(roll<acc)return p[i].id;}
  return p[p.length-1].id;
}

// ═══════════════════════════════════════
// INVENTORY & EQUIPMENT
// ═══════════════════════════════════════
var invSortMode='rarity';
function setSortMode(m){
  invSortMode=m;
  document.querySelectorAll('.sort-btn').forEach(function(b,i){b.className='sort-btn'+((['rarity','type','new'])[i]===m?' on':'');});
  updateInvGrid();
}

var rarityOrder={mythic:0,legendary:1,epic:2,rare:3,uncommon:4,common:5};
function getSortedInv(){
  var arr=P.inventory.slice();
  if(invSortMode==='rarity'){arr.sort(function(a,b){var ia=ITEMS[a.id],ib=ITEMS[b.id];if(!ia||!ib)return 0;return (rarityOrder[ia.r]||5)-(rarityOrder[ib.r]||5);});}
  else if(invSortMode==='type'){arr.sort(function(a,b){var ia=ITEMS[a.id],ib=ITEMS[b.id];if(!ia||!ib)return 0;return ia.t.localeCompare(ib.t);});}
  else if(invSortMode==='new'){arr.sort(function(a,b){return invAddOrder.indexOf(b.uid)-invAddOrder.indexOf(a.uid);});}
  return arr;
}

function updateInvGrid(){
  var grid=document.getElementById('inv-grid');if(!grid)return;
  grid.innerHTML='';
  document.getElementById('inv-count').textContent=P.inventory.length;
  var sorted=getSortedInv();
  sorted.forEach(function(entry){
    var item=ITEMS[entry.id];if(!item)return;
    var isEq=isEquipped(entry.id);
    var cell=document.createElement('div');
    cell.className='item-cell rc-'+item.r+(isEq?' equipped':'');
    cell.innerHTML='<div class="item-cell-icon">'+item.i+'</div><div class="item-cell-name r-'+item.r+'">'+esc(item.n)+'</div>';
    if(isEq)cell.innerHTML+='<div style="position:absolute;top:3px;right:3px;font-size:8px;color:#27ae60">✓</div>';
    (function(uid){cell.addEventListener('click',function(){openItemModal(uid);});})(entry.uid);
    grid.appendChild(cell);
  });
  document.getElementById('inv-gold-val').textContent='💰 '+fmt(P.gold)+'g';
}

function isEquipped(itemId){
  for(var s in P.equipped)if(P.equipped[s]===itemId)return true;
  return false;
}

function updateEquipSlots(){
  var slots={weapon:{icon:'⚔'},armor:{icon:'🛡'},helmet:{icon:'⛑'},ring:{icon:'💍'},gloves:{icon:'🧤'},pants:{icon:'👖'},boots:{icon:'👢'},amulet:{icon:'📿'}};
  for(var slot in slots){
    var id=P.equipped[slot];
    var iconEl=document.getElementById('eq-'+slot+'-icon');
    var nameEl=document.getElementById('eq-'+slot+'-name');
    var slotEl=document.getElementById('eq-'+slot);
    if(!iconEl)continue;
    if(id&&ITEMS[id]){
      var item=ITEMS[id];
      iconEl.textContent=item.i;
      iconEl.className='eq-slot-icon r-'+item.r;
      if(nameEl){nameEl.textContent=item.n;nameEl.className='eq-slot-name r-'+item.r;}
      if(slotEl)slotEl.className='eq-slot'+(slot==='ring'||slot==='amulet'?' eq-center':'')+' has-item';
    } else {
      iconEl.textContent=slots[slot].icon;
      iconEl.className='eq-slot-empty';
      if(nameEl){nameEl.textContent='';nameEl.className='';}
      if(slotEl)slotEl.className='eq-slot'+(slot==='ring'||slot==='amulet'?' eq-center':'');
    }
  }
}

function updateInvStats(){
  recalcStats();
  document.getElementById('st-lv').textContent=P.level;
  document.getElementById('st-hp').textContent=Math.ceil(P.hp)+'/'+P.maxHp;
  document.getElementById('st-base-atk').textContent=P.baseAtk||P.atk;
  document.getElementById('st-bonus-atk').textContent=P.bonusAtk>0?' (+'+P.bonusAtk+')':'';
  document.getElementById('st-base-def').textContent=P.baseDef||P.def;
  document.getElementById('st-bonus-def').textContent=P.bonusDef>0?' (+'+P.bonusDef+')':'';
  document.getElementById('st-crit').textContent=P.crit+'%';
  document.getElementById('st-kills').textContent=P.totalKills;
  document.getElementById('st-gold').textContent=fmt(P.gold);
  updateEquipSlots();
}

function openEqSlot(slot){
  var id=P.equipped[slot];
  if(!id){
    // Show items of this slot type
    var matching=P.inventory.filter(function(e){return ITEMS[e.id]&&ITEMS[e.id].t===slot;});
    if(!matching.length){toast('Нет предметов для слота '+slot,'#555');return;}
    openItemModal(matching[0].uid);
  } else {
    openItemModal(id);
  }
}

function openItemModal(uid){
  var entry=P.inventory.find(function(x){return x.uid===uid||x.id===uid;});
  if(!entry){for(var s in P.equipped){if(P.equipped[s]===uid){entry={id:uid,uid:uid};break;}}}
  if(!entry)return;
  var item=ITEMS[entry.id];if(!item)return;
  var isEq=isEquipped(entry.id);
  var inner=document.getElementById('imodal-inner');
  inner.innerHTML=
    '<div class="imodal-icon r-'+item.r+'">'+item.i+'</div>'
    +'<div class="imodal-name r-'+item.r+'">'+esc(item.n)+'</div>'
    +'<div class="imodal-rarity"><span class="ibadge badge-'+item.r+'">'+RARITY_LABEL[item.r]+'</span> | Слот: '+item.t+'</div>'
    +'<div class="imodal-desc">'+esc(item.desc||'')+'</div>'
    +'<div class="imodal-stats">'
    +(item.atk?'<div class="imodal-stat"><div class="imodal-stat-label">Атака</div><div class="imodal-stat-val">'+(item.atk>0?'+':'')+item.atk+'</div></div>':'')
    +(item.def?'<div class="imodal-stat"><div class="imodal-stat-label">Защита</div><div class="imodal-stat-val">+'+item.def+'</div></div>':'')
    +(item.hp?'<div class="imodal-stat"><div class="imodal-stat-label">HP</div><div class="imodal-stat-val">'+(item.hp>0?'+':'')+item.hp+'</div></div>':'')
    +(item.crit?'<div class="imodal-stat"><div class="imodal-stat-label">Крит%</div><div class="imodal-stat-val">+'+item.crit+'%</div></div>':'')
    +'</div>'
    +'<div class="imodal-btns">'
    +(isEq
      ?'<button class="imbtn-eq" onclick="unequipItem(\\''+entry.uid+'\\',\\''+entry.id+'\\')">Снять</button>'
      :'<button class="imbtn-eq" onclick="equipItem(\\''+entry.uid+'\\',\\''+entry.id+'\\')">Надеть</button>')
    +'<button class="imbtn-sell" onclick="sellItem(\\''+entry.uid+'\\')">Продать ('+item.sell+'g)</button>'
    +'<button class="imbtn-cls" onclick="closeItemModal()">Закрыть</button>'
    +'</div>';
  document.getElementById('item-modal-bg').className='on';
}
function closeItemModal(){document.getElementById('item-modal-bg').className='';}

function equipItem(uid,itemId){
  var item=ITEMS[itemId];if(!item)return;
  P.equipped[item.t]=itemId;
  recalcStats();updateEquipSlots();updateInvGrid();updateInvStats();updateHdr();closeItemModal();
  toast('Надето: '+item.n);
}
function unequipItem(uid,itemId){
  var item=ITEMS[itemId];if(!item)return;
  P.equipped[item.t]=null;
  recalcStats();updateEquipSlots();updateInvGrid();updateInvStats();updateHdr();closeItemModal();
  toast('Снято: '+item.n);
}
function sellItem(uid){
  var idx=P.inventory.findIndex(function(x){return x.uid===uid;});
  if(idx===-1)return;
  var item=ITEMS[P.inventory[idx].id];if(!item)return;
  for(var s in P.equipped){if(P.equipped[s]===P.inventory[idx].id)P.equipped[s]=null;}
  P.gold+=item.sell;
  P.inventory.splice(idx,1);
  recalcStats();updateEquipSlots();updateInvGrid();updateInvStats();updateHdr();closeItemModal();
  toast('+'+item.sell+' золота','#c9a227');
  if(curTab==='shop')document.getElementById('shop-gold').textContent=fmt(P.gold);
}

// ═══════════════════════════════════════
// TALENTS
// ═══════════════════════════════════════
function buildTalentTree(){updateTalentTree();}
function updateTalentTree(){
  var pts=P.talentPoints||0;
  document.getElementById('talent-pts-big').textContent=pts;
  var nextLv=P.level+1;
  document.getElementById('next-talent-lv').textContent='Lv.'+nextLv;
  if(document.getElementById('h-tp-wrap'))document.getElementById('h-tp-wrap').style.display=pts>0?'':'none';
  if(document.getElementById('h-tp'))document.getElementById('h-tp').textContent=pts;

  var tree=document.getElementById('talent-tree');if(!tree)return;
  // Group by branch
  var branches={};
  TALENT_DEFS.forEach(function(t){if(!branches[t.branch])branches[t.branch]=[];branches[t.branch].push(t);});
  tree.innerHTML='';
  for(var branch in branches){
    var sec=document.createElement('div');sec.className='talent-branch';
    sec.innerHTML='<div class="talent-branch-title">'+branch+'</div><div class="talent-row" id="tbr-'+branch+'"></div>';
    tree.appendChild(sec);
    var row=sec.querySelector('.talent-row');
    branches[branch].forEach(function(td){
      var lv=P.talents[td.id]||0;
      var maxed=lv>=td.maxLv;
      var canUnlock=pts>=(td.costPer||1)&&!maxed;
      var node=document.createElement('div');
      node.className='talent-node'+(maxed?' unlocked':(!canUnlock?' locked-talent':''));
      node.innerHTML=(lv>0?'<div class="talent-node-lvl">'+lv+'/'+td.maxLv+'</div>':'')
        +'<div class="talent-node-icon">'+td.icon+'</div>'
        +'<div class="talent-node-name">'+esc(td.name)+'</div>'
        +'<div class="talent-node-desc">'+esc(td.desc)+'</div>'
        +'<div class="talent-node-cost">'+(maxed?'✓ Максимум':(lv>0?'Улучшить: '+(td.costPer||1)+' ТО':'Изучить: '+(td.costPer||1)+' ТО'))+'</div>';
      if(!maxed&&canUnlock)(function(tid,cost){node.addEventListener('click',function(){learnTalent(tid,cost);});})(td.id,td.costPer||1);
      row.appendChild(node);
    });
  }
}
function learnTalent(id,cost){
  if((P.talentPoints||0)<cost){toast('Нужно '+cost+' очков таланта','#e74c3c');return;}
  var td=TALENT_DEFS.find(function(t){return t.id===id;});
  if(!td)return;
  if(!P.talents)P.talents={};
  var cur=P.talents[id]||0;
  if(cur>=td.maxLv){toast('Максимальный уровень!');return;}
  P.talentPoints-=cost;
  P.talents[id]=(cur+1);
  recalcStats();updateHdr();updateTalentTree();
  toast('Изучено: '+td.name+' ('+P.talents[id]+'/'+td.maxLv+')','#c9a227');
}

// ═══════════════════════════════════════
// SHOP / CASES
// ═══════════════════════════════════════
function buildShop(){
  var grid=document.getElementById('cases-grid');if(!grid)return;
  grid.innerHTML='';
  CASES.forEach(function(c){
    var card=document.createElement('div');
    card.className='case-card';
    card.style.borderColor=c.color+'40';
    var rarityBadges=c.rarities.map(function(r){return '<span class="case-rarity-badge badge-'+r+'">'+RARITY_LABEL[r]+'</span>';}).join('');
    card.innerHTML='<div class="case-icon" style="filter:drop-shadow(0 4px 12px '+c.color+'80)">'+c.icon+'</div>'
      +'<div class="case-name">'+esc(c.name)+'</div>'
      +'<div class="case-desc">'+esc(c.desc)+'</div>'
      +'<div class="case-contents">'+rarityBadges+'</div>'
      +'<div class="case-price">💰 '+fmt(c.price)+' золота</div>'
      +'<button class="case-open-btn" onclick="openCase(\\''+c.id+'\\')">Открыть</button>';
    grid.appendChild(card);
  });
}

function openCase(caseId){
  var c=CASES.find(function(x){return x.id===caseId;});if(!c)return;
  if(P.gold<c.price){toast('Мало золота! Нужно '+fmt(c.price),'#e74c3c');return;}
  P.gold-=c.price;updateHdr();
  if(curTab==='shop')document.getElementById('shop-gold').textContent=fmt(P.gold);
  // Pick random pool from case pools
  var pool=pick(c.pools);
  // Pick item from pool
  var itemId=tryDropForced(pool);
  if(!itemId){var fallbacks=Object.keys(ITEMS);itemId=pick(fallbacks);}
  var item=ITEMS[itemId];
  // Build reel with decoys + winning item
  showCaseReel(item,itemId,c);
}

function tryDropForced(poolKey){
  var p=ITEM_POOLS[poolKey];if(!p||!p.length)return null;
  var tot=p.reduce(function(s,x){return s+x.w;},0);
  var roll=Math.random()*tot,acc=0;
  for(var i=0;i<p.length;i++){acc+=p[i].w;if(roll<acc)return p[i].id;}
  return p[p.length-1].id;
}

function showCaseReel(winItem,winId,caseObj){
  var modal=document.getElementById('case-modal-bg');
  var content=document.getElementById('case-modal-content');
  modal.className='on';

  // Build reel — 30 items, winning item at position 24
  var allIds=Object.keys(ITEMS);
  var reelItems=[];
  for(var i=0;i<30;i++){
    var rid=i===24?winId:pick(allIds);
    reelItems.push(rid);
  }

  var reelHtml='<div style="font-size:16px;font-weight:bold;color:var(--gold);text-align:center;margin-bottom:12px">Открываем: '+esc(caseObj.name)+'</div>'
    +'<div class="case-reel-wrap">'
    +'<div class="case-reel-inner" id="case-reel">';
  reelItems.forEach(function(rid){
    var it=ITEMS[rid]||{i:'?',n:'?',r:'common'};
    reelHtml+='<div class="reel-item rc-'+it.r+'">'
      +'<div class="reel-item-icon">'+it.i+'</div>'
      +'<div class="reel-item-name r-'+it.r+'">'+esc(it.n)+'</div>'
      +'</div>';
  });
  reelHtml+='</div><div class="case-reel-arrow"></div></div>';
  content.innerHTML=reelHtml;

  // Animate
  setTimeout(function(){
    var reel=document.getElementById('case-reel');if(!reel)return;
    var itemW=106; // 100px + 6px gap
    var targetPos=-(24*itemW - (reel.parentElement.offsetWidth/2 - 50));
    reel.style.transition='transform 3.5s cubic-bezier(0.12,0.85,0.25,1)';
    reel.style.transform='translateX('+targetPos+'px)';
    setTimeout(function(){showCaseResult(winItem,winId,caseObj);},4000);
  },100);
}

function showCaseResult(item,itemId,caseObj){
  var content=document.getElementById('case-modal-content');
  var uid=Date.now()+'_'+Math.random().toString(36).slice(2,7);
  P.inventory.push({id:itemId,uid:uid,ts:Date.now()});
  invAddOrder.push(uid);

  content.innerHTML='<div class="case-result-reveal">'
    +'<div class="case-result-icon r-'+item.r+'" style="font-size:72px;text-align:center">'+item.i+'</div>'
    +'<div class="case-result-name r-'+item.r+'">'+esc(item.n)+'</div>'
    +'<div style="text-align:center;margin:6px 0"><span class="ibadge badge-'+item.r+'">'+RARITY_LABEL[item.r]+'</span></div>'
    +'<div class="case-result-desc">'+esc(item.desc||'')+'</div>'
    +'<div class="case-result-stats">'
    +(item.atk?'<span style="color:#e67e22">ATK +'+(item.atk>0?'+':'')+item.atk+'</span>':'')
    +(item.def?'<span style="color:#3498db">DEF +'+item.def+'</span>':'')
    +(item.hp?'<span style="color:#27ae60">HP '+(item.hp>0?'+':'')+item.hp+'</span>':'')
    +'</div>'
    +'<button class="case-result-btn" onclick="closeCaseModal()">Забрать!</button>'
    +'</div>';
  if(item.r==='legendary'||item.r==='mythic')toast('🎉 '+item.n+' ['+RARITY_LABEL[item.r]+']!','#c9a227');
}

function closeCaseModal(){document.getElementById('case-modal-bg').className='';updateInvGrid&&updateInvGrid();}

// ═══════════════════════════════════════
// ONLINE RAIDS
// ═══════════════════════════════════════
var activeRaidId=null,raidPollTimer=null;
var RBOSSINFO={
  forest_boss:{name:'Лесной Король', icon:'🌿',reqLv:5, hp:1000,desc:'Древний дух леса'},
  cave_boss:  {name:'Горный Дракон', icon:'🐲',reqLv:10,hp:2500,desc:'Страж подземелья'},
  abyss_boss: {name:'Повелитель Тьмы',icon:'👿',reqLv:18,hp:5000,desc:'Источник всего зла'},
};
var selectedBossId='forest_boss';

function buildRaids(){
  var panel=document.getElementById('p-raid');if(!panel)return;
  panel.innerHTML='';
  // Boss selector
  var create=document.createElement('div');create.className='raid-card';
  create.innerHTML='<h3>Создать рейд</h3>'
    +'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px" id="boss-btns"></div>'
    +'<button class="raid-btn" onclick="createRaid()">Создать рейд</button>';
  panel.appendChild(create);
  var bb=create.querySelector('#boss-btns');
  Object.keys(RBOSSINFO).forEach(function(bid){
    var b=RBOSSINFO[bid];var locked=P.level<b.reqLv;
    var btn=document.createElement('div');
    btn.style.cssText='background:'+(selectedBossId===bid?'rgba(92,61,143,.3)':'#0d0d18')+';border:1px solid '+(selectedBossId===bid?'#7c6af7':'#2a2540')+';border-radius:9px;padding:10px 14px;cursor:'+(locked?'not-allowed':'pointer')+';opacity:'+(locked?.4:1)+';flex:1;min-width:140px';
    btn.innerHTML='<div style="font-size:22px">'+b.icon+'</div><div style="font-size:12px;font-weight:bold;color:#d4c9a8;margin-top:3px">'+esc(b.name)+'</div><div style="font-size:10px;color:#666;margin-top:2px">HP: '+fmt(b.hp)+(locked?' | Ур.'+b.reqLv+'+':'')+'</div>';
    if(!locked)(function(id){btn.onclick=function(){selectedBossId=id;buildRaids();};})(bid);
    bb.appendChild(btn);
  });

  // Active raids list
  var listSec=document.createElement('div');listSec.className='raid-card';
  listSec.innerHTML='<h3>Открытые рейды <button onclick="loadRaidList()" style="font-size:11px;background:transparent;border:1px solid #444;color:#888;padding:2px 8px;border-radius:5px;cursor:pointer">Обновить</button></h3>'
    +'<div id="raid-list-wrap" class="raid-open-list"><div style="color:#555;font-size:13px">Загрузка...</div></div>'
    +'<div style="margin-top:10px;display:flex;gap:8px">'
    +'<input id="raid-code-inp" placeholder="Код рейда (напр. AB12CD)" style="flex:1;padding:8px;border-radius:8px;border:1px solid #2a2540;background:#0d0d18;color:#d4c9a8;font-size:13px;outline:none">'
    +'<button class="raid-btn" onclick="joinByCode()" style="padding:8px 14px;white-space:nowrap">Войти по коду</button>'
    +'</div>';
  panel.appendChild(listSec);

  if(activeRaidId){var room=document.createElement('div');room.className='raid-card';room.id='raid-room';panel.appendChild(room);renderRaidRoom(null);}
  loadRaidList();
}

async function loadRaidList(){
  var wrap=document.getElementById('raid-list-wrap');if(!wrap)return;
  try{
    var raids=await api('/api/raid/list');
    wrap.innerHTML='';
    if(!raids.length){wrap.innerHTML='<div style="color:#555;font-size:13px">Нет рейдов — создай!</div>';return;}
    raids.forEach(function(r){
      var b=RBOSSINFO[r.boss_id]||{icon:'?'};
      var pct=Math.round(r.boss_hp/r.boss_max_hp*100);
      var row=document.createElement('div');row.className='raid-list-row';
      row.innerHTML='<span style="font-size:20px">'+b.icon+'</span>'
        +'<div style="flex:1"><div style="font-size:13px;font-weight:bold;color:#d4c9a8">'+esc(b.name||r.boss_name)+' <span style="font-size:10px;color:#c9a227;background:#1a1408;padding:1px 6px;border-radius:4px">'+r.raid_id+'</span></div>'
        +'<div style="font-size:10px;color:#666;margin-top:2px">HP: '+fmt(r.boss_hp)+' | Игроков: '+r.member_count+' | '+(r.status==='waiting'?'<span style="color:#27ae60">Ожидание</span>':'<span style="color:#e67e22">Бой</span>')+'</div>'
        +'<div style="height:4px;background:#1a1a2e;border-radius:2px;margin-top:4px"><div style="width:'+pct+'%;height:4px;background:#c0392b;border-radius:2px"></div></div>'
        +'</div>'
        +'<button onclick="joinRaid(\\''+r.raid_id+'\\')" style="padding:6px 12px;border-radius:7px;border:none;background:#5c3d8f;color:#fff;font-size:12px;cursor:pointer">Войти</button>';
      wrap.appendChild(row);
    });
  }catch(e){if(wrap)wrap.innerHTML='<div style="color:#555;font-size:13px">Ошибка</div>';}
}

async function createRaid(){
  var b=RBOSSINFO[selectedBossId];
  if(P.level<(b?.reqLv||0)){toast('Нужен уровень '+b.reqLv,'#e74c3c');return;}
  if(P.hp<=0){toast('Нет HP!','#e74c3c');return;}
  try{var res=await api('/api/raid/create',{login:curUser.login,passhash:curUser.passhash,boss_id:selectedBossId});activeRaidId=res.raid_id;toast('Рейд создан! Код: '+res.raid_id);buildRaids();startRaidPoll();}
  catch(e){toast(e.message,'#e74c3c');}
}
async function joinRaid(rid){
  if(P.hp<=0){toast('Нет HP!','#e74c3c');return;}
  try{await api('/api/raid/join',{login:curUser.login,passhash:curUser.passhash,raid_id:rid});activeRaidId=rid;toast('Вошёл!');buildRaids();startRaidPoll();}
  catch(e){toast(e.message,'#e74c3c');}
}
function joinByCode(){var c=document.getElementById('raid-code-inp').value.trim().toUpperCase();if(!c){toast('Введи код','#e74c3c');return;}joinRaid(c);}
async function startRaidNow(){try{await api('/api/raid/start',{login:curUser.login,passhash:curUser.passhash,raid_id:activeRaidId});toast('Рейд начался!');}catch(e){toast(e.message,'#e74c3c');}}

function startRaidPoll(){if(raidPollTimer)clearInterval(raidPollTimer);raidPollTimer=setInterval(pollRaid,2500);}
async function pollRaid(){
  if(!activeRaidId)return;
  try{var s=await api('/api/raid/state?raid_id='+activeRaidId+'&login='+encodeURIComponent(curUser.login)+'&passhash='+encodeURIComponent(curUser.passhash));renderRaidRoom(s);
    if(s.status==='finished'){clearInterval(raidPollTimer);raidPollTimer=null;if(s.win&&s.gold_gain){P.gold+=s.gold_gain;if(s.xp_gain)gainXP(s.xp_gain);updateHdr();}}}
  catch(e){}
}

function leaveRaid(){if(raidPollTimer){clearInterval(raidPollTimer);raidPollTimer=null;}activeRaidId=null;var r=document.getElementById('raid-room');if(r)r.remove();loadRaidList();}

function renderRaidRoom(state){
  var room=document.getElementById('raid-room');if(!room)return;
  if(!state){room.innerHTML='<h3>Рейд: '+activeRaidId+' <button onclick="leaveRaid()" style="font-size:11px;background:transparent;border:1px solid #e74c3c;color:#e74c3c;padding:2px 8px;border-radius:5px;cursor:pointer">Покинуть</button></h3><div style="color:#555;padding:10px">Загрузка...</div>';return;}
  var binfo=RBOSSINFO[state.boss_id]||{icon:'👹'};
  var bpct=Math.max(0,Math.round(state.boss_hp/state.boss_max_hp*100));
  var canAtk=state.status==='active'&&state.my_hp>0&&(state.cooldown_left||0)<100&&!state.win&&!state.lose;
  var membersHtml=(state.members||[]).map(function(m){var mpct=Math.max(0,Math.round(m.hp/m.max_hp*100));return '<div class="pm'+(m.is_me?' is-me':'')+'">'+'<div class="pm-name">'+esc(m.nick)+'</div>'+'<div style="font-size:10px;color:#666">'+m.hp+'/'+m.max_hp+'</div>'+(m.hp<=0?'<div style="font-size:10px;color:#e74c3c">ПОГИБ</div>':'')+'<div class="pm-hp-bar"><div class="pm-hp-fill '+(m.is_me?'pm-hp-fill-me':'pm-hp-fill-ally')+'" style="width:'+mpct+'%"></div></div>'+'</div>';}).join('');
  var logHtml=(state.log||[]).slice(-15).map(function(l){var c=l.type==='atk'?'#e67e22':l.type==='win'?'#c9a227':l.type==='die'?'#e74c3c':'#555';return '<div style="color:'+c+'">'+esc(l.text)+'</div>';}).join('');
  room.innerHTML=
    '<h3>'+binfo.icon+' '+esc(state.boss_name)+' | <span style="color:var(--gold)">'+activeRaidId+'</span>'
    +'<button onclick="leaveRaid()" style="font-size:11px;background:transparent;border:1px solid #e74c3c;color:#e74c3c;padding:2px 8px;border-radius:5px;cursor:pointer">Покинуть</button></h3>'
    +'<div style="font-size:11px;color:#888;margin-bottom:4px;display:flex;justify-content:space-between"><span>HP Босса</span><span>'+fmt(state.boss_hp)+'/'+fmt(state.boss_max_hp)+'</span></div>'
    +'<div class="raid-boss-bar"><div class="raid-boss-bar-fill" style="width:'+bpct+'%"></div></div>'
    +'<div class="raid-party-row" style="margin:10px 0">'+membersHtml+'</div>'
    +'<div class="raid-log" id="raid-log-room">'+logHtml+'</div>'
    +(state.status==='waiting'
      ?'<div style="display:flex;gap:8px;margin-top:10px;align-items:center"><button class="raid-btn" onclick="startRaidNow()">Начать бой</button><span style="font-size:12px;color:#555">Код: <b style="color:var(--gold)">'+activeRaidId+'</b> — поделись с другом</span></div>'
      :state.win?'<div style="color:var(--gold);font-weight:bold;font-size:15px;text-align:center;padding:10px">ПОБЕДА! +'+fmt(state.gold_gain)+' золота, +'+state.xp_gain+' XP!</div>'
      :state.lose?'<div style="color:#e74c3c;font-weight:bold;font-size:15px;text-align:center;padding:10px">Поражение...</div>'
      :'<div style="display:flex;gap:8px;margin-top:10px"><button class="raid-btn" onclick="raidAtk(false)" '+(canAtk?'':'disabled')+'>Атака</button><button class="raid-btn raid-skill-btn" onclick="raidAtk(true)" '+(canAtk?'':'disabled')+'>Навык</button>'+(state.cooldown_left>100?'<span style="font-size:11px;color:#555;padding:9px 0">Перезарядка...</span>':'')+'</div>');
  var logEl=document.getElementById('raid-log-room');if(logEl)logEl.scrollTop=logEl.scrollHeight;
}

async function raidAtk(skill){
  if(!activeRaidId)return;
  try{var res=await api('/api/raid/attack',{login:curUser.login,passhash:curUser.passhash,raid_id:activeRaidId,skill:skill});
    if(res.state){renderRaidRoom(res.state);if(res.state.status==='finished'){clearInterval(raidPollTimer);raidPollTimer=null;if(res.state.win){P.gold+=res.state.gold_gain||0;if(res.state.xp_gain)gainXP(res.state.xp_gain);updateHdr();toast('Победа! +'+fmt(res.state.gold_gain)+' золота','#c9a227');}}}
  }catch(e){if(e.message&&e.message.includes('2'))return;toast(e.message,'#e74c3c');}
}

// ═══════════════════════════════════════
// CHAT
// ═══════════════════════════════════════
var lastChatLen=-1;
async function loadChat(){try{var msgs=await api('/api/chat');if(msgs.length===lastChatLen)return;lastChatLen=msgs.length;var box=document.getElementById('chat-box');var atBot=(box.scrollHeight-box.scrollTop-box.clientHeight)<80;box.innerHTML='';var now=Date.now();msgs.forEach(function(m){var mine=curUser&&m.nick===curUser.nick;var ago=Math.floor((now-m.ts)/1000);var agoStr=ago<60?ago+'с':Math.floor(ago/60)+'м';var div=document.createElement('div');div.className='cmsg'+(mine?' mine':'');var top=document.createElement('div');top.className='cmsg-top';top.innerHTML='<span class="cmsg-nick">'+esc(m.nick)+'</span><span class="cmsg-time">'+agoStr+' назад</span>';var txt=document.createElement('div');txt.className='cmsg-text';txt.textContent=m.text;div.appendChild(top);div.appendChild(txt);box.appendChild(div);});if(atBot)box.scrollTop=box.scrollHeight;document.getElementById('chat-status').textContent='Чат всех игроков | '+msgs.length+' сообщений';}catch(e){document.getElementById('chat-status').textContent='Чат недоступен';}}
async function sendMsg(){if(!curUser)return;var inp=document.getElementById('chat-inp');var text=inp.value.trim();if(!text)return;inp.value='';try{await api('/api/chat',{login:curUser.login,passhash:curUser.passhash,message:text});lastChatLen=-1;await loadChat();}catch(e){toast('Ошибка','#e74c3c');}}

// ═══════════════════════════════════════
// FRIENDS
// ═══════════════════════════════════════
async function loadFriends(){
  try{
    var data=await api('/api/friends?login='+encodeURIComponent(curUser.login)+'&passhash='+encodeURIComponent(curUser.passhash));
    var reqBox=document.getElementById('friend-reqs');
    if(data.requests&&data.requests.length){reqBox.innerHTML='';data.requests.forEach(function(r){var row=document.createElement('div');row.className='req-row';row.innerHTML='<span class="req-nick">'+esc(r.nick)+' ('+esc(r.login)+')</span><button class="req-btn acc" onclick="answerReq(\\''+esc(r.login)+'\\',true)">Принять</button><button class="req-btn dec" onclick="answerReq(\\''+esc(r.login)+'\\',false)">Отклонить</button>';reqBox.appendChild(row);});}
    else reqBox.innerHTML='<div style="color:#444;font-size:13px">Нет заявок</div>';
    var fBox=document.getElementById('friend-list'),sel=document.getElementById('transfer-to'),prev=sel.value;
    sel.innerHTML='<option value="">-- выбери друга --</option>';
    if(data.friends&&data.friends.length){fBox.innerHTML='';data.friends.forEach(function(f){var frow=document.createElement('div');frow.className='friend-row';frow.innerHTML='<div><div class="friend-nick">'+esc(f.nick)+'</div><div class="friend-info">Золото: '+fmt(f.earned||0)+'</div></div><button class="fbtn2 red" onclick="removeFriend(\\''+esc(f.login)+'\\')">Удалить</button>';fBox.appendChild(frow);var opt=document.createElement('option');opt.value=f.login;opt.textContent=f.nick;sel.appendChild(opt);});if(prev)sel.value=prev;}
    else fBox.innerHTML='<div style="color:#444;font-size:13px">Пока нет друзей</div>';
  }catch(e){}
}
async function sendFriendReq(){var login=document.getElementById('add-login').value.trim().toLowerCase();if(!login){toast('Введи логин','#e74c3c');return;}try{await api('/api/friends/add',{login:curUser.login,passhash:curUser.passhash,target_login:login});document.getElementById('add-login').value='';toast('Заявка отправлена!');loadFriends();}catch(e){toast(e.message,'#e74c3c');}}
async function answerReq(fl,accept){try{await api('/api/friends/answer',{login:curUser.login,passhash:curUser.passhash,from_login:fl,accept:accept});toast(accept?'Друг добавлен!':'Отклонено');loadFriends();}catch(e){toast(e.message,'#e74c3c');}}
async function removeFriend(fl){if(!confirm('Удалить?'))return;try{await api('/api/friends/remove',{login:curUser.login,passhash:curUser.passhash,friend_login:fl});toast('Удалено');loadFriends();}catch(e){toast(e.message,'#e74c3c');}}
async function doTransfer(){
  var to=document.getElementById('transfer-to').value;
  var amt=parseInt(document.getElementById('transfer-amt').value)||0;
  if(!to){toast('Выбери друга','#e74c3c');return;}
  if(amt<1){toast('Укажи сумму','#e74c3c');return;}
  if(P.gold<amt){toast('Мало золота! Есть: '+fmt(P.gold),'#e74c3c');return;}
  if(!confirm('Перевести '+fmt(amt)+' золота?'))return;
  try{
    await api('/api/friends/transfer',{login:curUser.login,passhash:curUser.passhash,to_login:to,amount:amt});
    P.gold-=amt;updateHdr();toast('Переведено '+fmt(amt)+' золота!','#27ae60');
    document.getElementById('transfer-amt').value='';
  }catch(e){toast(e.message,'#e74c3c');}
}

// ═══════════════════════════════════════
// LEADERBOARD
// ═══════════════════════════════════════
async function loadLead(){
  var wrap=document.getElementById('lead-wrap');wrap.innerHTML='<div style="color:#555;padding:20px;text-align:center">Загрузка...</div>';
  try{
    var rows=await api('/api/leaderboard');wrap.innerHTML='';
    if(!rows.length){wrap.innerHTML='<div style="color:#555;padding:20px;text-align:center">Пока никого нет</div>';return;}
    rows.forEach(function(r,i){
      var mine=curUser&&r.nick===curUser.nick;
      var row=document.createElement('div');row.className='lrow'+(mine?' me':'');
      row.innerHTML='<div class="lpos">'+(i===0?'🥇':i===1?'🥈':i===2?'🥉':(i+1)+'.')+'</div>'
        +'<div class="lname">'+(mine?'⭐ ':'')+esc(r.nick)+'</div>'
        +'<div><div class="lscore">Ур.'+r.level+' | '+fmt(r.kills)+' убийств</div><div class="lsub">'+fmt(r.gold)+' золота</div></div>';
      wrap.appendChild(row);
    });
  }catch(e){wrap.innerHTML='<div style="color:#e74c3c;padding:20px;text-align:center">Ошибка</div>';}
}
</script>
</body>
</html>
"""


def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        nick TEXT NOT NULL,
        passhash TEXT NOT NULL,
        created INTEGER NOT NULL,
        game_data TEXT DEFAULT '{}'
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nick TEXT NOT NULL,
        message TEXT NOT NULL,
        ts INTEGER NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_login TEXT NOT NULL,
        to_login TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        created INTEGER NOT NULL,
        UNIQUE(from_login, to_login)
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS raids (
        id TEXT PRIMARY KEY,
        boss_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'waiting',
        boss_hp INTEGER NOT NULL,
        boss_max_hp INTEGER NOT NULL,
        state TEXT NOT NULL DEFAULT '{}',
        created INTEGER NOT NULL,
        updated INTEGER NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS raid_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        raid_id TEXT NOT NULL,
        login TEXT NOT NULL,
        nick TEXT NOT NULL,
        hp INTEGER NOT NULL,
        max_hp INTEGER NOT NULL,
        atk INTEGER NOT NULL,
        def_val INTEGER NOT NULL,
        last_action INTEGER NOT NULL DEFAULT 0,
        UNIQUE(raid_id, login)
    )""")
    conn.commit()
    conn.close()

init_db()

def hash_pass(password: str, login: str) -> str:
    return hashlib.sha256((password + login + "clicker_salt_2024").encode()).hexdigest()

class RegisterData(BaseModel):
    login: str
    password: str
    nick: str

class LoginData(BaseModel):
    login: str
    password: str

class SaveData(BaseModel):
    login: str
    passhash: str
    game_data: dict

class ChatMessage(BaseModel):
    login: str
    passhash: str
    message: str

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML

@app.post("/api/register")
async def register(data: RegisterData):
    if len(data.login) < 3:
        raise HTTPException(400, "Логин слишком короткий (мин. 3 символа)")
    if len(data.password) < 3:
        raise HTTPException(400, "Пароль слишком короткий (мин. 3 символа)")
    if len(data.nick) < 2:
        raise HTTPException(400, "Никнейм слишком короткий (мин. 2 символа)")
    login = data.login.lower().strip()
    conn = db()
    try:
        if conn.execute("SELECT id FROM users WHERE login=?", (login,)).fetchone():
            raise HTTPException(400, "Такой логин уже занят")
        ph = hash_pass(data.password, login)
        conn.execute("INSERT INTO users (login,nick,passhash,created,game_data) VALUES (?,?,?,?,?)",
                   (login, data.nick.strip(), ph, int(time.time()*1000), "{}"))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "nick": data.nick.strip(), "passhash": ph, "login": login, "game_data": {}}

@app.post("/api/login")
async def login_user(data: LoginData):
    login = data.login.lower().strip()
    conn = db()
    try:
        user = conn.execute("SELECT * FROM users WHERE login=?", (login,)).fetchone()
        if not user:
            raise HTTPException(400, "Пользователь не найден")
        if user["passhash"] != hash_pass(data.password, login):
            raise HTTPException(400, "Неверный пароль")
        gd = json.loads(user["game_data"] or "{}")
        result = {"ok": True, "nick": user["nick"], "passhash": user["passhash"], "login": login, "game_data": gd}
    finally:
        conn.close()
    return result

@app.post("/api/save")
async def save_game(data: SaveData):
    login = data.login.lower().strip()
    conn = db()
    try:
        user = conn.execute("SELECT passhash FROM users WHERE login=?", (login,)).fetchone()
        if not user or user["passhash"] != data.passhash:
            raise HTTPException(403, "Ошибка авторизации")
        conn.execute("UPDATE users SET game_data=? WHERE login=?", (json.dumps(data.game_data), login))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.get("/api/leaderboard")
async def leaderboard():
    conn = db()
    try:
        rows = conn.execute("SELECT nick, game_data FROM users").fetchall()
        result = []
        for r in rows:
            gd = json.loads(r["game_data"] or "{}")
            level = gd.get("level", 1)
            kills = gd.get("totalKills", 0)
            gold = gd.get("gold", 0)
            if level > 1 or kills > 0 or gold > 0:
                result.append({"nick": r["nick"], "level": level, "kills": kills, "gold": gold, "earned": gold})
    finally:
        conn.close()
    result.sort(key=lambda x: (x["level"], x["kills"]), reverse=True)
    return result[:20]

@app.get("/api/chat")
async def get_chat():
    conn = db()
    try:
        rows = conn.execute("SELECT nick, message, ts FROM chat ORDER BY ts DESC LIMIT 100").fetchall()
        result = [{"nick": r["nick"], "text": r["message"], "ts": r["ts"]} for r in reversed(rows)]
    finally:
        conn.close()
    return result

@app.post("/api/chat")
async def post_chat(data: ChatMessage):
    login = data.login.lower().strip()
    conn = db()
    try:
        user = conn.execute("SELECT nick, passhash FROM users WHERE login=?", (login,)).fetchone()
        if not user or user["passhash"] != data.passhash:
            raise HTTPException(403, "Ошибка авторизации")
        msg = data.message.strip()
        if not msg or len(msg) > 300:
            raise HTTPException(400, "Неверное сообщение")
        conn.execute("INSERT INTO chat (nick, message, ts) VALUES (?,?,?)",
                   (user["nick"], msg, int(time.time()*1000)))
        conn.execute("DELETE FROM chat WHERE id NOT IN (SELECT id FROM chat ORDER BY ts DESC LIMIT 200)")
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

# ── FRIENDS ──────────────────────────────────────────────────

class FriendAdd(BaseModel):
    login: str
    passhash: str
    target_login: str

class FriendAnswer(BaseModel):
    login: str
    passhash: str
    from_login: str
    accept: bool

class FriendRemove(BaseModel):
    login: str
    passhash: str
    friend_login: str

class TransferData(BaseModel):
    login: str
    passhash: str
    to_login: str
    amount: float

def auth_user(login, passhash, conn):
    u = conn.execute("SELECT * FROM users WHERE login=?", (login,)).fetchone()
    if not u or u["passhash"] != passhash:
        raise HTTPException(403, "Ошибка авторизации")
    return u

@app.get("/api/friends")
async def get_friends(login: str, passhash: str):
    conn = db()
    try:
        u = auth_user(login.lower().strip(), passhash, conn)
        me = login.lower().strip()
        # incoming pending requests
        reqs = conn.execute(
            "SELECT f.from_login, u.nick FROM friends f JOIN users u ON u.login=f.from_login WHERE f.to_login=? AND f.status='pending'",
            (me,)).fetchall()
        requests = [{"login": r["from_login"], "nick": r["nick"]} for r in reqs]
        # accepted friends (either direction)
        rows = conn.execute("""
            SELECT u.login, u.nick, u.game_data FROM friends f
            JOIN users u ON (u.login = CASE WHEN f.from_login=? THEN f.to_login ELSE f.from_login END)
            WHERE (f.from_login=? OR f.to_login=?) AND f.status='accepted'
        """, (me, me, me)).fetchall()
        friends = []
        for r in rows:
            gd = json.loads(r["game_data"] or "{}")
            friends.append({"login": r["login"], "nick": r["nick"],
                            "earned": gd.get("totalEarned", 0), "cps": gd.get("autoCPS", 0)})
    finally:
        conn.close()
    return {"requests": requests, "friends": friends}

@app.post("/api/friends/add")
async def add_friend(data: FriendAdd):
    me = data.login.lower().strip()
    target = data.target_login.lower().strip()
    if me == target:
        raise HTTPException(400, "Нельзя добавить себя")
    conn = db()
    try:
        auth_user(me, data.passhash, conn)
        if not conn.execute("SELECT id FROM users WHERE login=?", (target,)).fetchone():
            raise HTTPException(400, "Игрок не найден")
        # check already friends or pending
        existing = conn.execute(
            "SELECT status FROM friends WHERE (from_login=? AND to_login=?) OR (from_login=? AND to_login=?)",
            (me, target, target, me)).fetchone()
        if existing:
            if existing["status"] == "accepted":
                raise HTTPException(400, "Уже в друзьях")
            raise HTTPException(400, "Заявка уже отправлена")
        conn.execute("INSERT INTO friends (from_login, to_login, status, created) VALUES (?,?,'pending',?)",
                    (me, target, int(time.time()*1000)))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.post("/api/friends/answer")
async def answer_friend(data: FriendAnswer):
    me = data.login.lower().strip()
    frm = data.from_login.lower().strip()
    conn = db()
    try:
        auth_user(me, data.passhash, conn)
        req = conn.execute(
            "SELECT id FROM friends WHERE from_login=? AND to_login=? AND status='pending'",
            (frm, me)).fetchone()
        if not req:
            raise HTTPException(400, "Заявка не найдена")
        if data.accept:
            conn.execute("UPDATE friends SET status='accepted' WHERE id=?", (req["id"],))
        else:
            conn.execute("DELETE FROM friends WHERE id=?", (req["id"],))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.post("/api/friends/remove")
async def remove_friend(data: FriendRemove):
    me = data.login.lower().strip()
    fr = data.friend_login.lower().strip()
    conn = db()
    try:
        auth_user(me, data.passhash, conn)
        conn.execute(
            "DELETE FROM friends WHERE (from_login=? AND to_login=?) OR (from_login=? AND to_login=?)",
            (me, fr, fr, me))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.post("/api/friends/transfer")
async def transfer(data: TransferData):
    me = data.login.lower().strip()
    to = data.to_login.lower().strip()
    amt = int(data.amount)
    if amt < 1:
        raise HTTPException(400, "Минимум 1 монета")
    conn = db()
    try:
        u = auth_user(me, data.passhash, conn)
        # check are friends
        fr = conn.execute(
            "SELECT id FROM friends WHERE ((from_login=? AND to_login=?) OR (from_login=? AND to_login=?)) AND status='accepted'",
            (me, to, to, me)).fetchone()
        if not fr:
            raise HTTPException(400, "Этот игрок не в друзьях")
        # deduct from sender
        gd_me = json.loads(u["game_data"] or "{}")
        coins_me = float(gd_me.get("gold", gd_me.get("coins", 0)))
        if coins_me < amt:
            raise HTTPException(400, "Недостаточно золота")
        gd_me["gold"] = coins_me - amt
        conn.execute("UPDATE users SET game_data=? WHERE login=?", (json.dumps(gd_me), me))
        # add to receiver
        rec = conn.execute("SELECT game_data FROM users WHERE login=?", (to,)).fetchone()
        if not rec:
            raise HTTPException(400, "Получатель не найден")
        gd_to = json.loads(rec["game_data"] or "{}")
        gd_to["gold"] = float(gd_to.get("gold", gd_to.get("coins", 0))) + amt
        conn.execute("UPDATE users SET game_data=? WHERE login=?", (json.dumps(gd_to), to))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}


# ── ONLINE RAIDS ─────────────────────────────────────────────

import random, string

RAID_BOSSES_DATA = {
    "forest_boss": {"name": "Лесной Король",  "hp": 1000, "atk": 35, "def": 10, "xp": 500,  "gold_min": 100, "gold_max": 300},
    "cave_boss":   {"name": "Горный Дракон",  "hp": 2500, "atk": 55, "def": 20, "xp": 1200, "gold_min": 300, "gold_max": 700},
    "abyss_boss":  {"name": "Повелитель Тьмы","hp": 5000, "atk": 80, "def": 35, "xp": 3000, "gold_min": 800, "gold_max": 2000},
}

def rand_id(n=6):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))

class RaidCreate(BaseModel):
    login: str
    passhash: str
    boss_id: str

class RaidJoin(BaseModel):
    login: str
    passhash: str
    raid_id: str

class RaidAttack(BaseModel):
    login: str
    passhash: str
    raid_id: str
    skill: bool = False

@app.post("/api/raid/create")
async def raid_create(data: RaidCreate):
    me = data.login.lower().strip()
    conn = db()
    try:
        u = auth_user(me, data.passhash, conn)
        boss = RAID_BOSSES_DATA.get(data.boss_id)
        if not boss:
            raise HTTPException(400, "Неизвестный босс")
        gd = json.loads(u["game_data"] or "{}")
        hp  = int(gd.get("hp", 100))
        mhp = int(gd.get("maxHp", 100))
        atk = int(gd.get("atk", 10))
        df  = int(gd.get("def", 5))
        if hp <= 0:
            raise HTTPException(400, "Нет HP для рейда")
        # Leave any existing waiting raids by this player
        conn.execute("""DELETE FROM raid_members WHERE login=? AND raid_id IN
            (SELECT id FROM raids WHERE status='waiting')""", (me,))
        # Create new raid
        rid = rand_id()
        now = int(time.time()*1000)
        conn.execute("INSERT INTO raids (id,boss_id,status,boss_hp,boss_max_hp,state,created,updated) VALUES (?,?,?,?,?,?,?,?)",
                    (rid, data.boss_id, "waiting", boss["hp"], boss["hp"], "{}", now, now))
        conn.execute("INSERT INTO raid_members (raid_id,login,nick,hp,max_hp,atk,def_val,last_action) VALUES (?,?,?,?,?,?,?,?)",
                    (rid, me, u["nick"], hp, mhp, atk, df, 0))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "raid_id": rid}

@app.post("/api/raid/join")
async def raid_join(data: RaidJoin):
    me = data.login.lower().strip()
    conn = db()
    try:
        u = auth_user(me, data.passhash, conn)
        raid = conn.execute("SELECT * FROM raids WHERE id=?", (data.raid_id,)).fetchone()
        if not raid:
            raise HTTPException(400, "Рейд не найден")
        if raid["status"] == "finished":
            raise HTTPException(400, "Рейд уже завершён")
        gd = json.loads(u["game_data"] or "{}")
        hp  = int(gd.get("hp", 100))
        mhp = int(gd.get("maxHp", 100))
        atk = int(gd.get("atk", 10))
        df  = int(gd.get("def", 5))
        if hp <= 0:
            raise HTTPException(400, "Нет HP для рейда")
        members = conn.execute("SELECT COUNT(*) as cnt FROM raid_members WHERE raid_id=?", (data.raid_id,)).fetchone()
        if members["cnt"] >= 6:
            raise HTTPException(400, "Рейд заполнен (макс 6)")
        try:
            conn.execute("INSERT INTO raid_members (raid_id,login,nick,hp,max_hp,atk,def_val,last_action) VALUES (?,?,?,?,?,?,?,?)",
                        (data.raid_id, me, u["nick"], hp, mhp, atk, df, 0))
        except:
            pass  # already in
        now = int(time.time()*1000)
        conn.execute("UPDATE raids SET updated=? WHERE id=?", (now, data.raid_id))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.post("/api/raid/start")
async def raid_start(data: RaidJoin):
    me = data.login.lower().strip()
    conn = db()
    try:
        auth_user(me, data.passhash, conn)
        raid = conn.execute("SELECT * FROM raids WHERE id=?", (data.raid_id,)).fetchone()
        if not raid:
            raise HTTPException(400, "Рейд не найден")
        if raid["status"] != "waiting":
            raise HTTPException(400, "Рейд уже начат")
        # Check creator is this user (first member)
        first = conn.execute("SELECT login FROM raid_members WHERE raid_id=? ORDER BY id ASC LIMIT 1", (data.raid_id,)).fetchone()
        if not first or first["login"] != me:
            raise HTTPException(403, "Только создатель может начать")
        now = int(time.time()*1000)
        conn.execute("UPDATE raids SET status='active', updated=? WHERE id=?", (now, data.raid_id))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.post("/api/raid/attack")
async def raid_attack(data: RaidAttack):
    me = data.login.lower().strip()
    conn = db()
    try:
        auth_user(me, data.passhash, conn)
        raid = conn.execute("SELECT * FROM raids WHERE id=?", (data.raid_id,)).fetchone()
        if not raid or raid["status"] != "active":
            raise HTTPException(400, "Рейд не активен")
        member = conn.execute("SELECT * FROM raid_members WHERE raid_id=? AND login=?",
                             (data.raid_id, me)).fetchone()
        if not member:
            raise HTTPException(400, "Ты не в этом рейде")
        if member["hp"] <= 0:
            raise HTTPException(400, "Ты погиб в рейде")
        now = int(time.time()*1000)
        if now - member["last_action"] < 2000:
            raise HTTPException(400, "Подожди 2 секунды")

        state = json.loads(raid["state"] or "{}")
        if "log" not in state:
            state["log"] = []

        boss_id   = raid["boss_id"]
        boss_data = RAID_BOSSES_DATA.get(boss_id, {})
        boss_hp   = raid["boss_hp"]
        boss_def  = boss_data.get("def", 10)
        boss_atk  = boss_data.get("atk", 30)

        # Player attacks boss
        atk_val = member["atk"] * (1.6 if data.skill else 1.0)
        dmg = max(1, int(atk_val - boss_def * 0.5) + random.randint(-3, 3))
        is_crit = random.random() < 0.15
        if is_crit:
            dmg = int(dmg * 1.8)
        boss_hp -= dmg

        action_desc = ("КРИТ! " if is_crit else "") + f"{member['nick']} {'навык' if data.skill else 'атакует'}: -{dmg} HP боссу"
        state["log"].append({"t": now, "text": action_desc, "type": "atk"})

        if boss_hp <= 0:
            boss_hp = 0
            # Victory
            gold_gain = random.randint(boss_data.get("gold_min", 50), boss_data.get("gold_max", 200))
            xp_gain   = boss_data.get("xp", 500)
            state["log"].append({"t": now, "text": f"БОСС ПОВЕРЖЕН! Каждый получает {gold_gain} золота и {xp_gain} XP!", "type": "win"})
            state["win"] = True
            state["gold_gain"] = gold_gain
            state["xp_gain"]   = xp_gain
            conn.execute("UPDATE raids SET boss_hp=?, status='finished', state=?, updated=? WHERE id=?",
                        (boss_hp, json.dumps(state), now, data.raid_id))
            # Give rewards to all living members
            members_all = conn.execute("SELECT login FROM raid_members WHERE raid_id=? AND hp>0", (data.raid_id,)).fetchall()
            for m in members_all:
                try:
                    u2 = conn.execute("SELECT game_data FROM users WHERE login=?", (m["login"],)).fetchone()
                    if u2:
                        gd2 = json.loads(u2["game_data"] or "{}")
                        gd2["gold"] = float(gd2.get("gold", 0)) + gold_gain
                        gd2["xp"]   = float(gd2.get("xp", 0)) + xp_gain
                        conn.execute("UPDATE users SET game_data=? WHERE login=?", (json.dumps(gd2), m["login"]))
                except:
                    pass
        else:
            # Boss attacks random alive member
            alive = conn.execute("SELECT * FROM raid_members WHERE raid_id=? AND hp>0", (data.raid_id,)).fetchall()
            if alive:
                target = random.choice(alive)
                bdmg = max(1, boss_atk - int(target["def_val"] * 0.5) + random.randint(-5, 5))
                new_hp = max(0, target["hp"] - bdmg)
                conn.execute("UPDATE raid_members SET hp=? WHERE raid_id=? AND login=?",
                            (new_hp, data.raid_id, target["login"]))
                state["log"].append({"t": now, "text": f"Босс атакует {target['nick']}: -{bdmg} HP", "type": "def"})
                if new_hp <= 0:
                    state["log"].append({"t": now, "text": f"{target['nick']} погиб!", "type": "die"})
                # Check all dead
                still_alive = conn.execute("SELECT COUNT(*) as cnt FROM raid_members WHERE raid_id=? AND hp>0", (data.raid_id,)).fetchone()
                if still_alive["cnt"] == 0:
                    state["log"].append({"t": now, "text": "Вся группа погибла! Рейд провален.", "type": "die"})
                    state["lose"] = True
                    conn.execute("UPDATE raids SET boss_hp=?, status='finished', state=?, updated=? WHERE id=?",
                                (boss_hp, json.dumps(state), now, data.raid_id))
                    conn.commit()
                    return {"ok": True, "state": await _get_raid_state(data.raid_id, me, conn)}
            conn.execute("UPDATE raids SET boss_hp=?, state=?, updated=? WHERE id=?",
                        (boss_hp, json.dumps(state), now, data.raid_id))

        conn.execute("UPDATE raid_members SET last_action=? WHERE raid_id=? AND login=?",
                    (now, data.raid_id, me))
        conn.commit()
        return {"ok": True, "state": await _get_raid_state(data.raid_id, me, conn)}
    finally:
        conn.close()

async def _get_raid_state(raid_id, me, conn):
    raid = conn.execute("SELECT * FROM raids WHERE id=?", (raid_id,)).fetchone()
    if not raid:
        return None
    members = conn.execute("SELECT * FROM raid_members WHERE raid_id=? ORDER BY id ASC", (raid_id,)).fetchall()
    boss_id  = raid["boss_id"]
    boss_info = RAID_BOSSES_DATA.get(boss_id, {})
    state = json.loads(raid["state"] or "{}")
    my_member = next((m for m in members if m["login"] == me), None)
    now = int(time.time()*1000)
    return {
        "raid_id":     raid_id,
        "boss_id":     boss_id,
        "boss_name":   boss_info.get("name", "Босс"),
        "boss_hp":     raid["boss_hp"],
        "boss_max_hp": raid["boss_max_hp"],
        "status":      raid["status"],
        "log":         state.get("log", [])[-20:],
        "win":         state.get("win", False),
        "lose":        state.get("lose", False),
        "gold_gain":   state.get("gold_gain", 0),
        "xp_gain":     state.get("xp_gain", 0),
        "my_hp":       my_member["hp"] if my_member else 0,
        "cooldown_left": max(0, 2000 - (now - (my_member["last_action"] if my_member else 0))),
        "members": [{"nick": m["nick"], "hp": m["hp"], "max_hp": m["max_hp"], "is_me": m["login"]==me} for m in members],
    }

@app.get("/api/raid/state")
async def raid_state(raid_id: str, login: str, passhash: str):
    me = login.lower().strip()
    conn = db()
    try:
        auth_user(me, passhash, conn)
        result = await _get_raid_state(raid_id, me, conn)
        if not result:
            raise HTTPException(404, "Рейд не найден")
        return result
    finally:
        conn.close()

@app.get("/api/raid/list")
async def raid_list():
    conn = db()
    try:
        rows = conn.execute("""SELECT r.id, r.boss_id, r.status, r.boss_hp, r.boss_max_hp,
            COUNT(rm.id) as member_count
            FROM raids r LEFT JOIN raid_members rm ON rm.raid_id=r.id
            WHERE r.status IN ('waiting','active')
            GROUP BY r.id ORDER BY r.created DESC LIMIT 20""").fetchall()
        result = []
        for r in rows:
            boss = RAID_BOSSES_DATA.get(r["boss_id"], {})
            result.append({
                "raid_id":      r["id"],
                "boss_id":      r["boss_id"],
                "boss_name":    boss.get("name","?"),
                "status":       r["status"],
                "boss_hp":      r["boss_hp"],
                "boss_max_hp":  r["boss_max_hp"],
                "member_count": r["member_count"],
            })
        return result
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

# ── ONLINE RAIDS ─────────────────────────────────────────────

import random, string

RAID_BOSSES_DATA = {
    "forest_boss": {"name": "Лесной Король",  "hp": 1000, "atk": 35, "def": 10, "xp": 500,  "gold_min": 100, "gold_max": 300},
    "cave_boss":   {"name": "Горный Дракон",  "hp": 2500, "atk": 55, "def": 20, "xp": 1200, "gold_min": 300, "gold_max": 700},
    "abyss_boss":  {"name": "Повелитель Тьмы","hp": 5000, "atk": 80, "def": 35, "xp": 3000, "gold_min": 800, "gold_max": 2000},
}

def rand_id(n=6):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=n))

class RaidCreate(BaseModel):
    login: str
    passhash: str
    boss_id: str

class RaidJoin(BaseModel):
    login: str
    passhash: str
    raid_id: str

class RaidAttack(BaseModel):
    login: str
    passhash: str
    raid_id: str
    skill: bool = False

@app.post("/api/raid/create")
async def raid_create(data: RaidCreate):
    me = data.login.lower().strip()
    conn = db()
    try:
        u = auth_user(me, data.passhash, conn)
        boss = RAID_BOSSES_DATA.get(data.boss_id)
        if not boss:
            raise HTTPException(400, "Неизвестный босс")
        gd = json.loads(u["game_data"] or "{}")
        hp  = int(gd.get("hp", 100))
        mhp = int(gd.get("maxHp", 100))
        atk = int(gd.get("atk", 10))
        df  = int(gd.get("def", 5))
        if hp <= 0:
            raise HTTPException(400, "Нет HP для рейда")
        # Leave any existing waiting raids by this player
        conn.execute("""DELETE FROM raid_members WHERE login=? AND raid_id IN
            (SELECT id FROM raids WHERE status='waiting')""", (me,))
        # Create new raid
        rid = rand_id()
        now = int(time.time()*1000)
        conn.execute("INSERT INTO raids (id,boss_id,status,boss_hp,boss_max_hp,state,created,updated) VALUES (?,?,?,?,?,?,?,?)",
                    (rid, data.boss_id, "waiting", boss["hp"], boss["hp"], "{}", now, now))
        conn.execute("INSERT INTO raid_members (raid_id,login,nick,hp,max_hp,atk,def_val,last_action) VALUES (?,?,?,?,?,?,?,?)",
                    (rid, me, u["nick"], hp, mhp, atk, df, 0))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "raid_id": rid}

@app.post("/api/raid/join")
async def raid_join(data: RaidJoin):
    me = data.login.lower().strip()
    conn = db()
    try:
        u = auth_user(me, data.passhash, conn)
        raid = conn.execute("SELECT * FROM raids WHERE id=?", (data.raid_id,)).fetchone()
        if not raid:
            raise HTTPException(400, "Рейд не найден")
        if raid["status"] == "finished":
            raise HTTPException(400, "Рейд уже завершён")
        gd = json.loads(u["game_data"] or "{}")
        hp  = int(gd.get("hp", 100))
        mhp = int(gd.get("maxHp", 100))
        atk = int(gd.get("atk", 10))
        df  = int(gd.get("def", 5))
        if hp <= 0:
            raise HTTPException(400, "Нет HP для рейда")
        members = conn.execute("SELECT COUNT(*) as cnt FROM raid_members WHERE raid_id=?", (data.raid_id,)).fetchone()
        if members["cnt"] >= 6:
            raise HTTPException(400, "Рейд заполнен (макс 6)")
        try:
            conn.execute("INSERT INTO raid_members (raid_id,login,nick,hp,max_hp,atk,def_val,last_action) VALUES (?,?,?,?,?,?,?,?)",
                        (data.raid_id, me, u["nick"], hp, mhp, atk, df, 0))
        except:
            pass  # already in
        now = int(time.time()*1000)
        conn.execute("UPDATE raids SET updated=? WHERE id=?", (now, data.raid_id))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.post("/api/raid/start")
async def raid_start(data: RaidJoin):
    me = data.login.lower().strip()
    conn = db()
    try:
        auth_user(me, data.passhash, conn)
        raid = conn.execute("SELECT * FROM raids WHERE id=?", (data.raid_id,)).fetchone()
        if not raid:
            raise HTTPException(400, "Рейд не найден")
        if raid["status"] != "waiting":
            raise HTTPException(400, "Рейд уже начат")
        # Check creator is this user (first member)
        first = conn.execute("SELECT login FROM raid_members WHERE raid_id=? ORDER BY id ASC LIMIT 1", (data.raid_id,)).fetchone()
        if not first or first["login"] != me:
            raise HTTPException(403, "Только создатель может начать")
        now = int(time.time()*1000)
        conn.execute("UPDATE raids SET status='active', updated=? WHERE id=?", (now, data.raid_id))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True}

@app.post("/api/raid/attack")
async def raid_attack(data: RaidAttack):
    me = data.login.lower().strip()
    conn = db()
    try:
        auth_user(me, data.passhash, conn)
        raid = conn.execute("SELECT * FROM raids WHERE id=?", (data.raid_id,)).fetchone()
        if not raid or raid["status"] != "active":
            raise HTTPException(400, "Рейд не активен")
        member = conn.execute("SELECT * FROM raid_members WHERE raid_id=? AND login=?",
                             (data.raid_id, me)).fetchone()
        if not member:
            raise HTTPException(400, "Ты не в этом рейде")
        if member["hp"] <= 0:
            raise HTTPException(400, "Ты погиб в рейде")
        now = int(time.time()*1000)
        if now - member["last_action"] < 2000:
            raise HTTPException(400, "Подожди 2 секунды")

        state = json.loads(raid["state"] or "{}")
        if "log" not in state:
            state["log"] = []

        boss_id   = raid["boss_id"]
        boss_data = RAID_BOSSES_DATA.get(boss_id, {})
        boss_hp   = raid["boss_hp"]
        boss_def  = boss_data.get("def", 10)
        boss_atk  = boss_data.get("atk", 30)

        # Player attacks boss
        atk_val = member["atk"] * (1.6 if data.skill else 1.0)
        dmg = max(1, int(atk_val - boss_def * 0.5) + random.randint(-3, 3))
        is_crit = random.random() < 0.15
        if is_crit:
            dmg = int(dmg * 1.8)
        boss_hp -= dmg

        action_desc = ("КРИТ! " if is_crit else "") + f"{member['nick']} {'навык' if data.skill else 'атакует'}: -{dmg} HP боссу"
        state["log"].append({"t": now, "text": action_desc, "type": "atk"})

        if boss_hp <= 0:
            boss_hp = 0
            # Victory
            gold_gain = random.randint(boss_data.get("gold_min", 50), boss_data.get("gold_max", 200))
            xp_gain   = boss_data.get("xp", 500)
            state["log"].append({"t": now, "text": f"БОСС ПОВЕРЖЕН! Каждый получает {gold_gain} золота и {xp_gain} XP!", "type": "win"})
            state["win"] = True
            state["gold_gain"] = gold_gain
            state["xp_gain"]   = xp_gain
            conn.execute("UPDATE raids SET boss_hp=?, status='finished', state=?, updated=? WHERE id=?",
                        (boss_hp, json.dumps(state), now, data.raid_id))
            # Give rewards to all living members
            members_all = conn.execute("SELECT login FROM raid_members WHERE raid_id=? AND hp>0", (data.raid_id,)).fetchall()
            for m in members_all:
                try:
                    u2 = conn.execute("SELECT game_data FROM users WHERE login=?", (m["login"],)).fetchone()
                    if u2:
                        gd2 = json.loads(u2["game_data"] or "{}")
                        gd2["gold"] = float(gd2.get("gold", 0)) + gold_gain
                        gd2["xp"]   = float(gd2.get("xp", 0)) + xp_gain
                        conn.execute("UPDATE users SET game_data=? WHERE login=?", (json.dumps(gd2), m["login"]))
                except:
                    pass
        else:
            # Boss attacks random alive member
            alive = conn.execute("SELECT * FROM raid_members WHERE raid_id=? AND hp>0", (data.raid_id,)).fetchall()
            if alive:
                target = random.choice(alive)
                bdmg = max(1, boss_atk - int(target["def_val"] * 0.5) + random.randint(-5, 5))
                new_hp = max(0, target["hp"] - bdmg)
                conn.execute("UPDATE raid_members SET hp=? WHERE raid_id=? AND login=?",
                            (new_hp, data.raid_id, target["login"]))
                state["log"].append({"t": now, "text": f"Босс атакует {target['nick']}: -{bdmg} HP", "type": "def"})
                if new_hp <= 0:
                    state["log"].append({"t": now, "text": f"{target['nick']} погиб!", "type": "die"})
                # Check all dead
                still_alive = conn.execute("SELECT COUNT(*) as cnt FROM raid_members WHERE raid_id=? AND hp>0", (data.raid_id,)).fetchone()
                if still_alive["cnt"] == 0:
                    state["log"].append({"t": now, "text": "Вся группа погибла! Рейд провален.", "type": "die"})
                    state["lose"] = True
                    conn.execute("UPDATE raids SET boss_hp=?, status='finished', state=?, updated=? WHERE id=?",
                                (boss_hp, json.dumps(state), now, data.raid_id))
                    conn.commit()
                    return {"ok": True, "state": await _get_raid_state(data.raid_id, me, conn)}
            conn.execute("UPDATE raids SET boss_hp=?, state=?, updated=? WHERE id=?",
                        (boss_hp, json.dumps(state), now, data.raid_id))

        conn.execute("UPDATE raid_members SET last_action=? WHERE raid_id=? AND login=?",
                    (now, data.raid_id, me))
        conn.commit()
        return {"ok": True, "state": await _get_raid_state(data.raid_id, me, conn)}
    finally:
        conn.close()

async def _get_raid_state(raid_id, me, conn):
    raid = conn.execute("SELECT * FROM raids WHERE id=?", (raid_id,)).fetchone()
    if not raid:
        return None
    members = conn.execute("SELECT * FROM raid_members WHERE raid_id=? ORDER BY id ASC", (raid_id,)).fetchall()
    boss_id  = raid["boss_id"]
    boss_info = RAID_BOSSES_DATA.get(boss_id, {})
    state = json.loads(raid["state"] or "{}")
    my_member = next((m for m in members if m["login"] == me), None)
    now = int(time.time()*1000)
    return {
        "raid_id":     raid_id,
        "boss_id":     boss_id,
        "boss_name":   boss_info.get("name", "Босс"),
        "boss_hp":     raid["boss_hp"],
        "boss_max_hp": raid["boss_max_hp"],
        "status":      raid["status"],
        "log":         state.get("log", [])[-20:],
        "win":         state.get("win", False),
        "lose":        state.get("lose", False),
        "gold_gain":   state.get("gold_gain", 0),
        "xp_gain":     state.get("xp_gain", 0),
        "my_hp":       my_member["hp"] if my_member else 0,
        "cooldown_left": max(0, 2000 - (now - (my_member["last_action"] if my_member else 0))),
        "members": [{"nick": m["nick"], "hp": m["hp"], "max_hp": m["max_hp"], "is_me": m["login"]==me} for m in members],
    }

@app.get("/api/raid/state")
async def raid_state(raid_id: str, login: str, passhash: str):
    me = login.lower().strip()
    conn = db()
    try:
        auth_user(me, passhash, conn)
        result = await _get_raid_state(raid_id, me, conn)
        if not result:
            raise HTTPException(404, "Рейд не найден")
        return result
    finally:
        conn.close()

@app.get("/api/raid/list")
async def raid_list():
    conn = db()
    try:
        rows = conn.execute("""SELECT r.id, r.boss_id, r.status, r.boss_hp, r.boss_max_hp,
            COUNT(rm.id) as member_count
            FROM raids r LEFT JOIN raid_members rm ON rm.raid_id=r.id
            WHERE r.status IN ('waiting','active')
            GROUP BY r.id ORDER BY r.created DESC LIMIT 20""").fetchall()
        result = []
        for r in rows:
            boss = RAID_BOSSES_DATA.get(r["boss_id"], {})
            result.append({
                "raid_id":      r["id"],
                "boss_id":      r["boss_id"],
                "boss_name":    boss.get("name","?"),
                "status":       r["status"],
                "boss_hp":      r["boss_hp"],
                "boss_max_hp":  r["boss_max_hp"],
                "member_count": r["member_count"],
            })
        return result
    finally:
        conn.close()



if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
