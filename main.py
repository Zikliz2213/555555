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
.sprite-body{font-size:52px;line-height:1;filter:drop-shadow(0 4px 8px rgba(0,0,0,.8));transition:transform .15s;display:flex;align-items:center;justify-content:center;width:80px;height:80px}
.sprite-body.attack-anim{animation:atk-anim .4s ease-out}
.sprite-body.hurt-anim{animation:hurt-anim .3s ease-out}
@keyframes atk-anim{0%{transform:translateX(0)}30%{transform:translateX(60px) scale(1.2)}60%{transform:translateX(30px)}100%{transform:translateX(0)}}
@keyframes hurt-anim{0%,100%{transform:translateX(0);filter:drop-shadow(0 4px 8px rgba(0,0,0,.8))}50%{transform:translateX(-8px);filter:drop-shadow(0 0 16px rgba(231,76,60,1)) brightness(2)}}
.sprite-name{font-size:11px;color:#aaa;font-weight:bold;background:rgba(0,0,0,.5);padding:2px 6px;border-radius:4px}
/* Enemy sprite */
.enemy-sprite{position:relative;z-index:3;display:flex;flex-direction:column;align-items:center;gap:4px}
.enemy-body{font-size:60px;line-height:1;filter:drop-shadow(0 4px 12px rgba(0,0,0,.9));transition:transform .15s;transform:scaleX(-1);display:flex;align-items:center;justify-content:center;width:80px;height:80px}
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
        <div class="hstat" id="h-pet-wrap" style="display:none">🐾<b id="h-pet-name" style="color:#27ae60"></b></div>
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
    <button class="tab"     onclick="goTab('clan')">⚜ Клан</button>
    <button class="tab"     onclick="goTab('chat')">💬 Чат</button>
    <button class="tab"     onclick="goTab('friends')">👥 Друзья</button>
    <button class="tab"     onclick="goTab('lead')">🏆 Топ</button>
  </div>

  <!-- WORLD MAP -->
  <div id="p-world" class="panel" style="display:flex">
    <!-- Map location tabs -->
    <div style="display:flex;gap:4px;margin-bottom:6px">
      <button id="maploc-village" class="sort-btn on" onclick="switchMapLoc('village')">🏘 Деревня</button>
      <button id="maploc-mountains" class="sort-btn" onclick="switchMapLoc('mountains')">⛰ Горы (Lv10+)</button>
    </div>
    <div id="world-map-wrap">
      <!-- VILLAGE MAP -->
      <svg id="map-village" id="world-svg" viewBox="0 0 860 420" xmlns="http://www.w3.org/2000/svg" style="width:100%;display:block">
        <defs>
          <radialGradient id="sky-grad" cx="50%" cy="30%" r="70%">
            <stop offset="0%" stop-color="#0d1a0d"/><stop offset="100%" stop-color="#080f08"/>
          </radialGradient>
          <radialGradient id="glow-forest" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#27ae60" stop-opacity=".5"/><stop offset="100%" stop-color="#27ae60" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="glow-cave" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#3498db" stop-opacity=".4"/><stop offset="100%" stop-color="#3498db" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="glow-ruins" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#e67e22" stop-opacity=".4"/><stop offset="100%" stop-color="#e67e22" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="glow-volcano" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#e74c3c" stop-opacity=".5"/><stop offset="100%" stop-color="#e74c3c" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="glow-abyss" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#9b59b6" stop-opacity=".6"/><stop offset="100%" stop-color="#9b59b6" stop-opacity="0"/>
          </radialGradient>
          <filter id="blur4"><feGaussianBlur stdDeviation="4"/></filter>
          <filter id="blur2"><feGaussianBlur stdDeviation="2"/></filter>
        </defs>
        <!-- Sky/ground -->
        <rect width="860" height="420" fill="url(#sky-grad)"/>
        <!-- Stars -->
        <circle cx="50" cy="20" r="1" fill="#fff" opacity=".5"/><circle cx="140" cy="12" r="1.5" fill="#fff" opacity=".4"/>
        <circle cx="240" cy="30" r="1" fill="#fff" opacity=".6"/><circle cx="500" cy="15" r="1" fill="#fff" opacity=".5"/>
        <circle cx="650" cy="25" r="1.5" fill="#fff" opacity=".4"/><circle cx="800" cy="18" r="1" fill="#fff" opacity=".6"/>
        <!-- Ground -->
        <rect x="0" y="310" width="860" height="110" fill="#0a1a08"/>
        <path d="M0 310 Q215 295 430 305 Q645 315 860 300 L860 320 Q645 335 430 325 Q215 315 0 330 Z" fill="#0d2010" opacity=".8"/>
        <!-- Dirt road horizontal -->
        <path d="M0 340 Q100 335 200 338 Q320 342 420 338 Q520 334 620 338 Q720 342 860 336" stroke="#1a1408" stroke-width="18" fill="none" opacity=".9"/>
        <path d="M0 340 Q100 335 200 338 Q320 342 420 338 Q520 334 620 338 Q720 342 860 336" stroke="#2a2010" stroke-width="10" fill="none" stroke-dasharray="12,6"/>
        <!-- Dirt road to forest (left branch) -->
        <path d="M90 338 Q80 320 75 300 Q70 280 68 255" stroke="#1a1408" stroke-width="10" fill="none"/>
        <path d="M90 338 Q80 320 75 300 Q70 280 68 255" stroke="#2a2010" stroke-width="5" fill="none" stroke-dasharray="8,5"/>

        <!-- ═══ VILLAGE BUILDINGS CENTER ═══ -->
        <!-- YOUR HOUSE -->
        <g class="map-zone-btn" id="mb-myhouse" onclick="openMyHouse()" style="cursor:pointer">
          <ellipse cx="310" cy="340" rx="40" ry="15" fill="#27ae60" opacity=".15" filter="url(#blur4)"/>
          <!-- House walls -->
          <rect x="285" y="295" width="50" height="40" fill="#2a1a0a" stroke="#3d2810" stroke-width="1.5"/>
          <!-- Roof -->
          <polygon points="280,296 335,296 310,268" fill="#5c2a0a" stroke="#7a3810" stroke-width="1"/>
          <!-- Door -->
          <rect x="302" y="315" width="16" height="20" rx="3" fill="#1a0f05" stroke="#5c3d1a" stroke-width="1"/>
          <circle cx="315" cy="326" r="1.5" fill="#c9a227"/>
          <!-- Window -->
          <rect x="288" y="302" width="10" height="9" rx="1" fill="#0d1a2e" stroke="#3d5068" stroke-width="1"/>
          <!-- Chimney -->
          <rect x="322" y="260" width="8" height="18" fill="#3a2010"/>
          <ellipse cx="326" cy="260" rx="5" ry="3" fill="#555" opacity=".6"/>
          <!-- Label -->
          <rect x="282" y="338" width="56" height="18" rx="4" fill="rgba(0,0,0,.75)" stroke="#27ae60" stroke-width="1"/>
          <text x="310" y="351" text-anchor="middle" fill="#27ae60" font-size="9" font-weight="bold" font-family="Arial">🏠 Мой дом</text>
        </g>

        <!-- SHOP -->
        <g class="map-zone-btn" id="mb-shop" onclick="openMapShop()" style="cursor:pointer">
          <ellipse cx="430" cy="340" rx="42" ry="15" fill="#c9a227" opacity=".15" filter="url(#blur4)"/>
          <rect x="403" y="292" width="54" height="43" fill="#1a1408" stroke="#3d2a10" stroke-width="1.5"/>
          <!-- Roof with awning -->
          <polygon points="398,293 457,293 430,265" fill="#4d1a08" stroke="#6d2a10" stroke-width="1"/>
          <!-- Awning -->
          <path d="M403 293 Q430 302 457 293" fill="#8b2010" opacity=".8"/>
          <!-- Shop sign -->
          <rect x="408" y="270" width="44" height="14" rx="3" fill="#1a0f05" stroke="#c9a227" stroke-width="1"/>
          <text x="430" y="281" text-anchor="middle" fill="#c9a227" font-size="8" font-weight="bold" font-family="Arial">МАГАЗИН</text>
          <!-- Door -->
          <rect x="420" y="313" width="20" height="22" rx="2" fill="#0d0a05" stroke="#4d3a1a" stroke-width="1"/>
          <!-- Windows -->
          <rect x="406" y="300" width="11" height="10" rx="1" fill="#0d1a2e" stroke="#3d5068" stroke-width="1"/>
          <rect x="440" y="300" width="11" height="10" rx="1" fill="#0d1a2e" stroke="#3d5068" stroke-width="1"/>
          <rect x="430" y="338" width="0" height="0"/>
          <rect x="385" y="337" width="90" height="18" rx="4" fill="rgba(0,0,0,.75)" stroke="#c9a227" stroke-width="1"/>
          <text x="430" y="350" text-anchor="middle" fill="#c9a227" font-size="9" font-weight="bold" font-family="Arial">🛒 Магазин</text>
        </g>

        <!-- FORGE / BLACKSMITH -->
        <g class="map-zone-btn" id="mb-forge" onclick="openForge()" style="cursor:pointer">
          <ellipse cx="550" cy="338" rx="42" ry="15" fill="#e67e22" opacity=".15" filter="url(#blur4)"/>
          <rect x="523" y="294" width="54" height="40" fill="#1a0f05" stroke="#3d1a05" stroke-width="1.5"/>
          <polygon points="518,295 577,295 550,268" fill="#3d1a05" stroke="#5d2a0a" stroke-width="1"/>
          <!-- Forge fire glow -->
          <ellipse cx="550" cy="295" rx="10" ry="6" fill="#ff6b1a" opacity=".5" filter="url(#blur2)"/>
          <!-- Anvil icon -->
          <rect x="536" y="308" width="28" height="8" rx="2" fill="#555"/>
          <rect x="540" y="300" width="20" height="8" rx="2" fill="#666"/>
          <rect x="545" y="316" width="10" height="6" fill="#444"/>
          <!-- Smoke -->
          <circle cx="548" cy="262" r="3" fill="#333" opacity=".5"/>
          <circle cx="552" cy="256" r="2.5" fill="#333" opacity=".4"/>
          <circle cx="546" cy="250" r="2" fill="#333" opacity=".3"/>
          <rect x="505" y="336" width="90" height="18" rx="4" fill="rgba(0,0,0,.75)" stroke="#e67e22" stroke-width="1"/>
          <text x="550" y="349" text-anchor="middle" fill="#e67e22" font-size="9" font-weight="bold" font-family="Arial">⚒ Кузня</text>
        </g>

        <!-- QUEST BOARD -->
        <g class="map-zone-btn" id="mb-quests" onclick="openQuestBoard()" style="cursor:pointer">
          <ellipse cx="185" cy="340" rx="38" ry="14" fill="#9b59b6" opacity=".15" filter="url(#blur4)"/>
          <!-- Post/board -->
          <rect x="180" y="275" width="5" height="60" fill="#3d2a10"/>
          <rect x="163" y="275" width="42" height="32" rx="3" fill="#2a1a08" stroke="#5c3d1a" stroke-width="1.5"/>
          <!-- Papers on board -->
          <rect x="166" y="278" width="14" height="10" rx="1" fill="#d4c9a8" opacity=".8"/>
          <rect x="183" y="278" width="18" height="10" rx="1" fill="#c4a060" opacity=".7"/>
          <rect x="166" y="292" width="35" height="10" rx="1" fill="#d4c9a8" opacity=".6"/>
          <!-- Exclamation -->
          <circle cx="185" cy="268" r="7" fill="#9b59b6" opacity=".9"/>
          <text x="185" y="272" text-anchor="middle" fill="#fff" font-size="10" font-weight="bold" font-family="Arial">!</text>
          <rect x="154" y="336" width="62" height="18" rx="4" fill="rgba(0,0,0,.75)" stroke="#9b59b6" stroke-width="1"/>
          <text x="185" y="349" text-anchor="middle" fill="#9b59b6" font-size="9" font-weight="bold" font-family="Arial">📋 Задания</text>
        </g>

        <!-- RAID PORTAL -->
        <g class="map-zone-btn" id="mb-raid-portal" onclick="goTab('raid')" style="cursor:pointer">
          <ellipse cx="680" cy="338" rx="38" ry="14" fill="#e74c3c" opacity=".2" filter="url(#blur4)"/>
          <ellipse cx="680" cy="318" rx="22" ry="28" fill="#0d0020" stroke="#5c3d8f" stroke-width="2" opacity=".9"/>
          <ellipse cx="680" cy="318" rx="16" ry="21" fill="#150030" stroke="#9b59b6" stroke-width="1.5" opacity=".8"/>
          <ellipse cx="680" cy="318" rx="8" ry="11" fill="#200040" opacity=".95"/>
          <circle cx="663" cy="305" r="2" fill="#9b59b6" opacity=".7"/><circle cx="697" cy="308" r="2" fill="#7c3ab0" opacity=".6"/>
          <circle cx="668" cy="330" r="1.5" fill="#b060ff" opacity=".8"/><circle cx="692" cy="328" r="2" fill="#9b59b6" opacity=".5"/>
          <rect x="648" y="336" width="64" height="18" rx="4" fill="rgba(0,0,0,.75)" stroke="#9b59b6" stroke-width="1"/>
          <text x="680" y="349" text-anchor="middle" fill="#9b59b6" font-size="9" font-weight="bold" font-family="Arial">🔥 Портал рейда</text>
        </g>

        <!-- TRADE NPC -->
        <g class="map-zone-btn" id="mb-trade" onclick="openTrade()" style="cursor:pointer">
          <ellipse cx="430" cy="200" rx="32" ry="12" fill="#3498db" opacity=".15" filter="url(#blur4)"/>
          <!-- NPC figure -->
          <circle cx="430" cy="178" r="9" fill="#c8956c"/>
          <rect x="422" y="186" width="16" height="14" rx="3" fill="#2980b9"/>
          <!-- Hat -->
          <rect x="423" y="171" width="14" height="5" rx="2" fill="#1a5a8a"/>
          <rect x="425" y="166" width="10" height="7" rx="2" fill="#1a5a8a"/>
          <!-- Sign with arrows -->
          <rect x="436" y="174" width="18" height="12" rx="2" fill="#1a1408" stroke="#3498db" stroke-width="1"/>
          <text x="445" y="184" text-anchor="middle" fill="#3498db" font-size="8" font-family="Arial">⇄</text>
          <rect x="400" y="197" width="60" height="16" rx="4" fill="rgba(0,0,0,.75)" stroke="#3498db" stroke-width="1"/>
          <text x="430" y="209" text-anchor="middle" fill="#3498db" font-size="9" font-weight="bold" font-family="Arial">🔄 Обмен</text>
        </g>

        <!-- PET TAMER NPC -->
        <g class="map-zone-btn" id="mb-pet" onclick="openPetShop()" style="cursor:pointer">
          <ellipse cx="310" cy="200" rx="32" ry="12" fill="#27ae60" opacity=".15" filter="url(#blur4)"/>
          <!-- NPC figure -->
          <circle cx="310" cy="178" r="9" fill="#c8a06c"/>
          <rect x="302" y="186" width="16" height="14" rx="3" fill="#1a5c28"/>
          <!-- Pet animal nearby -->
          <ellipse cx="326" cy="190" rx="7" ry="5" fill="#8b4513"/>
          <circle cx="331" cy="187" r="4" fill="#8b4513"/>
          <circle cx="333" cy="186" r="1.5" fill="#111"/>
          <polygon points="330,184 332,179 334,184" fill="#8b4513"/>
          <rect x="280" y="197" width="60" height="16" rx="4" fill="rgba(0,0,0,.75)" stroke="#27ae60" stroke-width="1"/>
          <text x="310" y="209" text-anchor="middle" fill="#27ae60" font-size="9" font-weight="bold" font-family="Arial">🐾 Питомцы</text>
        </g>

        <!-- ═══ FOREST ZONE (left) ═══ -->
        <g class="map-zone-btn" id="mz-forest" onclick="selectZone('forest')" data-zone="forest">
          <ellipse cx="68" cy="240" rx="62" ry="40" fill="url(#glow-forest)" class="zone-glow zone-pulse" filter="url(#blur4)"/>
          <polygon points="35,255 52,222 68,255" fill="#0d3d1a" opacity=".9"/>
          <polygon points="50,260 68,227 86,260" fill="#0a4d1a" opacity=".9"/>
          <polygon points="60,265 82,232 100,265" fill="#164d20" opacity=".8"/>
          <rect x="56" y="254" width="6" height="14" fill="#2d1a0a"/>
          <rect x="72" y="257" width="6" height="14" fill="#2d1a0a"/>
          <!-- Mobs outside -->
          <text x="28" y="218" font-size="14" opacity=".7" style="pointer-events:none">🐺</text>
          <text x="94" y="212" font-size="12" opacity=".6" style="pointer-events:none">👺</text>
          <rect x="18" y="268" width="100" height="20" rx="5" fill="rgba(0,0,0,.75)" stroke="#27ae60" stroke-width="1"/>
          <text x="68" y="282" text-anchor="middle" fill="#27ae60" font-size="10" font-weight="bold" font-family="Arial">🌲 Тёмный Лес</text>
        </g>
        <text x="68" y="298" text-anchor="middle" fill="#555" font-size="9" font-family="Arial">Lv.1+</text>

        <!-- ═══ CAVE ZONE ═══ -->
        <g class="map-zone-btn" id="mz-cave" onclick="selectZone('cave')" data-zone="cave">
          <ellipse cx="800" cy="240" rx="55" ry="40" fill="url(#glow-cave)" class="zone-glow" filter="url(#blur4)"/>
          <polygon points="762,258 782,218 802,258" fill="#1a1a2e" opacity=".9"/>
          <polygon points="778,258 798,220 818,258" fill="#1e1e35" opacity=".85"/>
          <ellipse cx="798" cy="256" rx="11" ry="7" fill="#050508"/>
          <!-- Mobs outside cave -->
          <text x="758" y="210" font-size="13" opacity=".7" style="pointer-events:none">💀</text>
          <text x="818" y="214" font-size="12" opacity=".6" style="pointer-events:none">🕷</text>
          <rect x="748" y="266" width="104" height="20" rx="5" fill="rgba(0,0,0,.75)" stroke="#3498db" stroke-width="1"/>
          <text x="800" y="280" text-anchor="middle" fill="#3498db" font-size="10" font-weight="bold" font-family="Arial">🕳 Пещера Ужаса</text>
        </g>
        <text x="800" y="296" text-anchor="middle" fill="#555" font-size="9" font-family="Arial">Lv.3+</text>
        <g id="lock-cave" style="display:none">
          <rect x="748" y="208" width="104" height="72" rx="6" fill="rgba(0,0,0,.75)"/>
          <text x="800" y="250" text-anchor="middle" fill="#555" font-size="22" font-family="Arial">🔒</text>
          <text x="800" y="268" text-anchor="middle" fill="#555" font-size="10" font-family="Arial">Ур.3</text>
        </g>

        <!-- ═══ RUINS ZONE (top-center) ═══ -->
        <g class="map-zone-btn" id="mz-ruins" onclick="selectZone('ruins')" data-zone="ruins">
          <ellipse cx="430" cy="165" rx="65" ry="38" fill="url(#glow-ruins)" class="zone-glow" filter="url(#blur4)"/>
          <rect x="398" y="148" width="10" height="30" fill="#2a1a0a" opacity=".9"/>
          <rect x="397" y="146" width="14" height="5" fill="#3a2510"/>
          <rect x="418" y="155" width="10" height="25" fill="#2a1a0a" opacity=".9"/>
          <rect x="416" y="153" width="14" height="5" fill="#3a2510"/>
          <rect x="438" y="143" width="10" height="35" fill="#2a1a0a" opacity=".9"/>
          <rect x="436" y="141" width="14" height="5" fill="#3a2510"/>
          <rect x="456" y="156" width="10" height="22" fill="#2a1a0a" opacity=".8"/>
          <rect x="393" y="176" width="80" height="5" fill="#1a1008" opacity=".7"/>
          <!-- Mobs outside ruins -->
          <text x="382" y="140" font-size="13" opacity=".65" style="pointer-events:none">🧟</text>
          <text x="470" y="138" font-size="12" opacity=".6" style="pointer-events:none">🧙</text>
          <rect x="372" y="183" width="116" height="20" rx="5" fill="rgba(0,0,0,.75)" stroke="#e67e22" stroke-width="1"/>
          <text x="430" y="197" text-anchor="middle" fill="#e67e22" font-size="10" font-weight="bold" font-family="Arial">🏛 Древние Руины</text>
        </g>
        <text x="430" y="212" text-anchor="middle" fill="#555" font-size="9" font-family="Arial">Lv.7+</text>
        <g id="lock-ruins" style="display:none">
          <rect x="372" y="128" width="116" height="80" rx="6" fill="rgba(0,0,0,.75)"/>
          <text x="430" y="172" text-anchor="middle" fill="#555" font-size="22" font-family="Arial">🔒</text>
          <text x="430" y="190" text-anchor="middle" fill="#555" font-size="10" font-family="Arial">Ур.7</text>
        </g>
        <!-- Road to ruins from village -->
        <path d="M430 225 Q430 260 430 295" stroke="#1a1408" stroke-width="8" fill="none" opacity=".6"/>
        <path d="M430 225 Q430 260 430 295" stroke="#2a2010" stroke-width="4" fill="none" stroke-dasharray="8,5"/>

        <!-- ═══ VOLCANO (top right) ═══ -->
        <g class="map-zone-btn" id="mz-volcano" onclick="selectZone('volcano')" data-zone="volcano">
          <ellipse cx="680" cy="155" rx="58" ry="38" fill="url(#glow-volcano)" class="zone-glow" filter="url(#blur4)"/>
          <polygon points="642,175 668,118 700,175" fill="#3d1a08" opacity=".95"/>
          <polygon points="655,175 682,122 710,175" fill="#4d2010" opacity=".9"/>
          <ellipse cx="680" cy="122" rx="10" ry="7" fill="#ff6b1a" opacity=".7" filter="url(#blur4)"/>
          <ellipse cx="680" cy="120" rx="5" ry="3" fill="#ffd166" opacity=".8"/>
          <path d="M670,138 Q667,150 670,158" stroke="#e67e22" stroke-width="2" fill="none" opacity=".6"/>
          <!-- Mobs outside volcano -->
          <text x="635" y="115" font-size="13" opacity=".7" style="pointer-events:none">🔥</text>
          <text x="715" y="118" font-size="12" opacity=".6" style="pointer-events:none">🐉</text>
          <rect x="630" y="180" width="100" height="20" rx="5" fill="rgba(0,0,0,.75)" stroke="#e74c3c" stroke-width="1"/>
          <text x="680" y="194" text-anchor="middle" fill="#e74c3c" font-size="10" font-weight="bold" font-family="Arial">🌋 Огненная Гора</text>
        </g>
        <text x="680" y="208" text-anchor="middle" fill="#555" font-size="9" font-family="Arial">Lv.12+</text>
        <g id="lock-volcano" style="display:none">
          <rect x="630" y="108" width="100" height="80" rx="6" fill="rgba(0,0,0,.75)"/>
          <text x="680" y="152" text-anchor="middle" fill="#555" font-size="22" font-family="Arial">🔒</text>
          <text x="680" y="170" text-anchor="middle" fill="#555" font-size="10" font-family="Arial">Ур.12</text>
        </g>
        <!-- Road volcano from village -->
        <path d="M550 295 Q600 260 640 215" stroke="#1a1408" stroke-width="8" fill="none" opacity=".6"/>
        <path d="M550 295 Q600 260 640 215" stroke="#2a2010" stroke-width="4" fill="none" stroke-dasharray="8,5"/>

        <!-- ═══ ABYSS (top left) ═══ -->
        <g class="map-zone-btn" id="mz-abyss" onclick="selectZone('abyss')" data-zone="abyss">
          <ellipse cx="185" cy="160" rx="55" ry="38" fill="url(#glow-abyss)" class="zone-glow" filter="url(#blur4)"/>
          <ellipse cx="185" cy="152" rx="25" ry="20" fill="#0d0020" stroke="#5c3d8f" stroke-width="2" opacity=".9"/>
          <ellipse cx="185" cy="152" rx="17" ry="13" fill="#150030" stroke="#9b59b6" stroke-width="1.5" opacity=".8"/>
          <ellipse cx="185" cy="152" rx="8" ry="6" fill="#200040" opacity=".95"/>
          <circle cx="167" cy="141" r="2" fill="#9b59b6" opacity=".7"/><circle cx="203" cy="144" r="2" fill="#7c3ab0" opacity=".6"/>
          <circle cx="172" cy="163" r="1.5" fill="#b060ff" opacity=".8"/><circle cx="198" cy="161" r="2" fill="#9b59b6" opacity=".5"/>
          <!-- Mobs outside abyss -->
          <text x="144" y="130" font-size="13" opacity=".7" style="pointer-events:none">😈</text>
          <text x="213" y="128" font-size="12" opacity=".6" style="pointer-events:none">☠</text>
          <rect x="140" y="182" width="90" height="20" rx="5" fill="rgba(0,0,0,.75)" stroke="#9b59b6" stroke-width="1"/>
          <text x="185" y="196" text-anchor="middle" fill="#9b59b6" font-size="10" font-weight="bold" font-family="Arial">🌀 Бездна</text>
        </g>
        <text x="185" y="210" text-anchor="middle" fill="#555" font-size="9" font-family="Arial">Lv.20+</text>
        <g id="lock-abyss" style="display:none">
          <rect x="140" y="120" width="90" height="78" rx="6" fill="rgba(0,0,0,.75)"/>
          <text x="185" y="163" text-anchor="middle" fill="#555" font-size="22" font-family="Arial">🔒</text>
          <text x="185" y="181" text-anchor="middle" fill="#555" font-size="10" font-family="Arial">Ур.20</text>
        </g>
        <!-- Road abyss from village -->
        <path d="M310 295 Q250 260 215 218" stroke="#1a1408" stroke-width="8" fill="none" opacity=".6"/>
        <path d="M310 295 Q250 260 215 218" stroke="#2a2010" stroke-width="4" fill="none" stroke-dasharray="8,5"/>

        <!-- Mountains transition (right edge) -->
        <g class="map-zone-btn" id="mb-mountains-gate" onclick="switchMapLoc('mountains')" style="cursor:pointer">
          <ellipse cx="800" cy="355" rx="38" ry="14" fill="#aaa" opacity=".1" filter="url(#blur4)"/>
          <!-- Mountain silhouette -->
          <polygon points="775,355 792,325 810,355" fill="#2a2a3a" opacity=".9"/>
          <polygon points="787,355 806,328 825,355" fill="#333345" opacity=".85"/>
          <!-- Snow caps -->
          <polygon points="788,332 792,325 796,332" fill="#eee" opacity=".7"/>
          <polygon points="802,335 806,328 810,335" fill="#eee" opacity=".6"/>
          <rect x="763" y="358" width="75" height="18" rx="4" fill="rgba(0,0,0,.8)" stroke="#aaa" stroke-width="1"/>
          <text x="800" y="371" text-anchor="middle" fill="#aaa" font-size="9" font-weight="bold" font-family="Arial">⛰ Горы (Lv10+)</text>
        </g>
        <g id="lock-mountains-gate" style="display:none">
          <rect x="763" y="318" width="75" height="55" rx="6" fill="rgba(0,0,0,.8)"/>
          <text x="800" y="348" text-anchor="middle" fill="#555" font-size="20" font-family="Arial">🔒</text>
          <text x="800" y="364" text-anchor="middle" fill="#555" font-size="9" font-family="Arial">Ур.10</text>
        </g>

        <!-- Current zone indicator -->
        <g id="map-current-marker" style="display:none">
          <circle r="8" fill="var(--gold)" opacity=".9">
            <animate attributeName="r" values="6;10;6" dur="1.5s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values=".9;.4;.9" dur="1.5s" repeatCount="indefinite"/>
          </circle>
          <text text-anchor="middle" dy="-14" fill="var(--gold)" font-size="10" font-weight="bold" font-family="Arial">ВЫ ЗДЕСЬ</text>
        </g>
      </svg>

      <!-- MOUNTAINS MAP (hidden by default) -->
      <svg id="map-mountains" viewBox="0 0 860 420" xmlns="http://www.w3.org/2000/svg" style="width:100%;display:none">
        <defs>
          <radialGradient id="sky-mtn" cx="50%" cy="30%" r="70%">
            <stop offset="0%" stop-color="#0f0f1a"/><stop offset="100%" stop-color="#0a0a14"/>
          </radialGradient>
          <filter id="blur4m"><feGaussianBlur stdDeviation="4"/></filter>
        </defs>
        <rect width="860" height="420" fill="url(#sky-mtn)"/>
        <!-- Snow / mist -->
        <circle cx="100" cy="50" r="40" fill="#fff" opacity=".03"/>
        <circle cx="400" cy="30" r="60" fill="#fff" opacity=".02"/>
        <circle cx="700" cy="55" r="45" fill="#fff" opacity=".03"/>
        <!-- Ground -->
        <rect x="0" y="320" width="860" height="100" fill="#12121e"/>
        <path d="M0 320 Q215 305 430 315 Q645 325 860 308 L860 325 L0 335 Z" fill="#1a1a2e" opacity=".8"/>

        <!-- Mountain background silhouette -->
        <polygon points="0,320 80,180 160,320" fill="#1a1a28" opacity=".7"/>
        <polygon points="120,320 240,130 360,320" fill="#1e1e32" opacity=".7"/>
        <polygon points="300,320 430,100 560,320" fill="#1a1a28" opacity=".8"/>
        <polygon points="500,320 620,155 740,320" fill="#1e1e32" opacity=".7"/>
        <polygon points="680,320 790,170 860,320" fill="#1a1a28" opacity=".7"/>
        <!-- Snow caps -->
        <polygon points="70,192 80,180 90,192" fill="#cce" opacity=".6"/>
        <polygon points="228,144 240,130 252,144" fill="#dde" opacity=".6"/>
        <polygon points="418,112 430,100 442,112" fill="#eef" opacity=".7"/>
        <polygon points="608,167 620,155 632,167" fill="#dde" opacity=".6"/>
        <polygon points="780,182 790,170 800,182" fill="#cce" opacity=".6"/>

        <!-- Road in mountains -->
        <path d="M0 355 Q215 345 430 350 Q645 355 860 345" stroke="#1a1a28" stroke-width="16" fill="none" opacity=".9"/>
        <path d="M0 355 Q215 345 430 350 Q645 355 860 345" stroke="#2a2a3e" stroke-width="8" fill="none" stroke-dasharray="12,6"/>

        <!-- DUNGEON ENTRANCE -->
        <g class="map-zone-btn" id="mz-mountains" onclick="selectZone('mountains')" data-zone="mountains" style="cursor:pointer">
          <ellipse cx="430" cy="340" rx="60" ry="20" fill="#3498db" opacity=".15" filter="url(#blur4m)"/>
          <!-- Stone arch dungeon -->
          <rect x="405" y="290" width="50" height="40" fill="#1a1a28" stroke="#2a2a3e" stroke-width="2"/>
          <path d="M405 290 Q430 268 455 290" fill="#0d0d1a" stroke="#2a2a3e" stroke-width="2"/>
          <!-- Dungeon entrance dark -->
          <ellipse cx="430" cy="292" rx="18" ry="14" fill="#050510"/>
          <ellipse cx="430" cy="294" rx="12" ry="10" fill="#030308"/>
          <!-- Torches -->
          <rect x="400" y="295" width="4" height="14" fill="#3d2810"/>
          <ellipse cx="402" cy="295" rx="3" ry="4" fill="#ff8c00" opacity=".8" filter="url(#blur4m)"/>
          <rect x="456" y="295" width="4" height="14" fill="#3d2810"/>
          <ellipse cx="458" cy="295" rx="3" ry="4" fill="#ff8c00" opacity=".8" filter="url(#blur4m)"/>
          <!-- Chains on arch -->
          <text x="414" y="288" font-size="8" fill="#555">⛓</text>
          <text x="440" y="288" font-size="8" fill="#555">⛓</text>
          <rect x="385" y="337" width="90" height="20" rx="5" fill="rgba(0,0,0,.8)" stroke="#3498db" stroke-width="1"/>
          <text x="430" y="351" text-anchor="middle" fill="#3498db" font-size="10" font-weight="bold" font-family="Arial">🏔 Горное подземелье</text>
        </g>
        <text x="430" y="366" text-anchor="middle" fill="#555" font-size="9" font-family="Arial">Lv.10+</text>

        <!-- MOUNTAIN BOSS -->
        <g class="map-zone-btn" id="mz-mountains_boss" onclick="selectZone('mountains_boss')" data-zone="mountains_boss" style="cursor:pointer">
          <ellipse cx="680" cy="310" rx="55" ry="20" fill="#e74c3c" opacity=".18" filter="url(#blur4m)"/>
          <!-- Boss lair -->
          <polygon points="645,320 665,270 695,320" fill="#3d1a1a" opacity=".95"/>
          <polygon points="660,320 680,265 700,320" fill="#4d2020" opacity=".9"/>
          <!-- Lava cracks -->
          <path d="M655,310 Q660,305 665,310" stroke="#e74c3c" stroke-width="1.5" fill="none" opacity=".7"/>
          <path d="M688,312 Q693,308 698,312" stroke="#ff6b1a" stroke-width="1.5" fill="none" opacity=".6"/>
          <!-- Boss skull -->
          <text x="672" y="282" font-size="16" opacity=".8" style="pointer-events:none">💀</text>
          <!-- Enemy mobs outside -->
          <text x="625" y="265" font-size="13" opacity=".7" style="pointer-events:none">🧊</text>
          <text x="718" y="268" font-size="12" opacity=".6" style="pointer-events:none">🐺</text>
          <rect x="637" y="322" width="86" height="20" rx="5" fill="rgba(0,0,0,.8)" stroke="#e74c3c" stroke-width="1"/>
          <text x="680" y="336" text-anchor="middle" fill="#e74c3c" font-size="10" font-weight="bold" font-family="Arial">💀 Логово Босса</text>
        </g>
        <text x="680" y="350" text-anchor="middle" fill="#555" font-size="9" font-family="Arial">Lv.15+</text>
        <g id="lock-mountains_boss" style="display:none">
          <rect x="637" y="255" width="86" height="74" rx="6" fill="rgba(0,0,0,.8)"/>
          <text x="680" y="297" text-anchor="middle" fill="#555" font-size="22" font-family="Arial">🔒</text>
          <text x="680" y="315" text-anchor="middle" fill="#555" font-size="9" font-family="Arial">Ур.15</text>
        </g>

        <!-- Return to village -->
        <g onclick="switchMapLoc('village')" style="cursor:pointer">
          <rect x="10" y="340" width="90" height="22" rx="6" fill="rgba(0,0,0,.8)" stroke="#555" stroke-width="1"/>
          <text x="55" y="355" text-anchor="middle" fill="#aaa" font-size="10" font-weight="bold" font-family="Arial">← Деревня</text>
        </g>

        <!-- Mountain mobs roaming -->
        <text x="150" y="310" font-size="16" opacity=".6" style="pointer-events:none">🧊</text>
        <text x="270" y="300" font-size="14" opacity=".5" style="pointer-events:none">🐺</text>
        <text x="560" y="308" font-size="15" opacity=".6" style="pointer-events:none">🦅</text>
        <text x="740" y="310" font-size="14" opacity=".5" style="pointer-events:none">🧊</text>

        <!-- Current zone marker (mountains) -->
        <g id="map-current-marker-mtn" style="display:none">
          <circle r="8" fill="var(--gold)" opacity=".9">
            <animate attributeName="r" values="6;10;6" dur="1.5s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values=".9;.4;.9" dur="1.5s" repeatCount="indefinite"/>
          </circle>
          <text text-anchor="middle" dy="-14" fill="var(--gold)" font-size="10" font-weight="bold" font-family="Arial">ВЫ ЗДЕСЬ</text>
        </g>
      </svg>

      <div id="map-tooltip"></div>
    </div>
    <!-- Zone info panel below map -->
    <div id="zone-info-panel" style="background:var(--card);border-radius:12px;border:1px solid var(--border);padding:14px;display:flex;align-items:center;gap:14px;margin-top:6px">
      <div style="font-size:36px" id="zi-icon">🌲</div>
      <div style="flex:1">
        <div style="font-size:15px;font-weight:bold;color:var(--gold)" id="zi-name">Тёмный Лес</div>
        <div style="font-size:12px;color:#666;margin-top:2px" id="zi-desc">Волки, гоблины и разбойники скрываются здесь</div>
        <div style="font-size:11px;color:#555;margin-top:4px" id="zi-enemies">Враги: Волк 🐺, Гоблин 👺, Разбойник 🗡</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:6px">
        <button onclick="goToBattle()" id="go-battle-btn" style="padding:10px 20px;border-radius:9px;border:none;background:var(--purple);color:#fff;font-size:13px;font-weight:bold;cursor:pointer">⚔ Сражаться</button>
        <button onclick="openDungeon()" id="go-dungeon-btn" style="padding:8px 20px;border-radius:9px;border:none;background:linear-gradient(135deg,#1a1a2e,#2a1a3e);color:#3498db;font-size:12px;font-weight:bold;cursor:pointer;border:1px solid #3498db">🏰 Подземелье</button>
      </div>
    </div>
  </div>

  <!-- DUNGEON MODAL -->
  <div id="dungeon-modal-bg" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.88);align-items:flex-start;justify-content:center;z-index:400;overflow-y:auto;padding:12px 0">
    <div style="background:#0d0d18;border:1px solid #2a2540;border-radius:16px;padding:0;max-width:540px;width:95%;margin:0 auto">
      <!-- Header -->
      <div style="padding:14px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between">
        <div>
          <div style="font-size:16px;font-weight:bold;color:var(--gold)" id="dng-title">🏰 Подземелье</div>
          <div style="font-size:11px;color:#555;margin-top:2px">Уровень <span id="dng-floor">1</span> · Комната <span id="dng-room">1</span>/<span id="dng-room-total">5</span></div>
        </div>
        <div style="display:flex;gap:8px;align-items:center">
          <div style="font-size:12px;color:#666">HP: <span id="dng-hp" style="color:#e74c3c;font-weight:bold">100</span></div>
          <button onclick="closeDungeon()" style="background:transparent;border:1px solid #444;color:#888;font-size:12px;cursor:pointer;padding:4px 10px;border-radius:6px">Выйти</button>
        </div>
      </div>
      <!-- Floor progress bar -->
      <div style="padding:8px 18px;border-bottom:1px solid var(--border)">
        <div style="display:flex;gap:4px" id="dng-progress-dots"></div>
      </div>
      <!-- Main dungeon area -->
      <div id="dng-main" style="padding:16px 18px"></div>
    </div>
  </div>

  <!-- MY HOUSE MODAL -->
  <div id="myhouse-modal-bg" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.8);align-items:center;justify-content:center;z-index:300">
    <div style="background:#12121e;border:1px solid #3a2560;border-radius:14px;padding:20px;max-width:400px;width:90%;max-height:85vh;overflow-y:auto">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div style="font-size:16px;font-weight:bold;color:var(--gold)">🏠 Твой дом</div>
        <button onclick="closeMyHouse()" style="background:transparent;border:none;color:#555;font-size:18px;cursor:pointer">✕</button>
      </div>
      <div style="font-size:12px;color:#666;margin-bottom:12px">Обустрой свой дом — мебель даёт постоянные бафы!</div>
      <div id="house-furniture-list"></div>
      <div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--border)">
        <div style="font-size:11px;color:#555;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px">Активные бафы дома</div>
        <div id="house-buffs-list" style="font-size:12px;color:var(--green)"></div>
      </div>
    </div>
  </div>

  <!-- FORGE MODAL -->
  <div id="forge-modal-bg" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.8);align-items:center;justify-content:center;z-index:300">
    <div style="background:#12121e;border:1px solid #5c2a0a;border-radius:14px;padding:20px;max-width:420px;width:90%;max-height:85vh;overflow-y:auto">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div style="font-size:16px;font-weight:bold;color:#e67e22">⚒ Кузня</div>
        <button onclick="closeForge()" style="background:transparent;border:none;color:#555;font-size:18px;cursor:pointer">✕</button>
      </div>
      <div style="font-size:12px;color:#666;margin-bottom:14px">Зачаруй снаряжение за золото. Зачарование даёт +5 ATK или +5 DEF на 1 бой (стакается 3 раза).</div>
      <div style="font-size:13px;font-weight:bold;color:#d4c9a8;margin-bottom:8px">Выбери предмет для зачарования:</div>
      <div id="forge-items-list"></div>
    </div>
  </div>

  <!-- QUEST BOARD MODAL -->
  <div id="quest-modal-bg" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.8);align-items:center;justify-content:center;z-index:300">
    <div style="background:#12121e;border:1px solid #3d2560;border-radius:14px;padding:20px;max-width:420px;width:90%;max-height:85vh;overflow-y:auto">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div style="font-size:16px;font-weight:bold;color:#9b59b6">📋 Доска заданий</div>
        <button onclick="closeQuestBoard()" style="background:transparent;border:none;color:#555;font-size:18px;cursor:pointer">✕</button>
      </div>
      <div id="quest-list"></div>
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
        <button class="sort-btn" style="color:#e67e22;border-color:#5a2a0a" onclick="sellAllUnequipped()">💰 Продать всё</button>
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

  <!-- CLAN -->
  <div id="p-clan" class="panel" style="flex-direction:column;gap:10px">
    <div id="clan-content"></div>
  </div>

  <!-- TRADE MODAL -->
  <div id="trade-modal-bg" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.85);align-items:center;justify-content:center;z-index:400">
    <div style="background:#12121e;border:1px solid #2a4a6a;border-radius:14px;padding:20px;max-width:420px;width:92%;max-height:85vh;overflow-y:auto">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div style="font-size:16px;font-weight:bold;color:#3498db">🔄 Обмен предметами</div>
        <button onclick="closeTrade()" style="background:transparent;border:none;color:#555;font-size:18px;cursor:pointer">✕</button>
      </div>
      <div style="font-size:12px;color:#666;margin-bottom:12px">Выбери предмет и укажи игрока для отправки. Получатель принимает/отклоняет обмен.</div>
      <div style="margin-bottom:10px">
        <div style="font-size:11px;color:#555;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px">Твой предмет для обмена:</div>
        <div id="trade-my-items" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(52px,1fr));gap:5px;max-height:160px;overflow-y:auto"></div>
      </div>
      <div id="trade-selected-item" style="margin-bottom:10px;display:none">
        <div style="font-size:11px;color:#27ae60;margin-bottom:4px">✓ Выбрано:</div>
        <div id="trade-selected-name" style="font-size:13px;font-weight:bold;color:#d4c9a8"></div>
      </div>
      <div style="margin-bottom:10px">
        <div style="font-size:11px;color:#555;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px">Кому отправить (логин):</div>
        <input id="trade-target-login" placeholder="Логин игрока" style="width:100%;padding:8px 10px;border-radius:8px;border:1px solid var(--border);background:#0d0d18;color:#d4c9a8;font-size:13px;outline:none">
      </div>
      <button onclick="sendTradeOffer()" style="width:100%;padding:10px;border-radius:9px;border:none;background:#2980b9;color:#fff;font-size:13px;font-weight:bold;cursor:pointer">📤 Отправить предложение</button>
      <div style="margin-top:14px;border-top:1px solid var(--border);padding-top:12px">
        <div style="font-size:11px;color:#555;text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">Входящие предложения:</div>
        <div id="trade-incoming"></div>
      </div>
    </div>
  </div>

  <!-- PET SHOP MODAL -->
  <div id="pet-modal-bg" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.85);align-items:center;justify-content:center;z-index:400">
    <div style="background:#12121e;border:1px solid #1a5c28;border-radius:14px;padding:20px;max-width:400px;width:92%;max-height:85vh;overflow-y:auto">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
        <div style="font-size:16px;font-weight:bold;color:#27ae60">🐾 Питомцы</div>
        <button onclick="closePetShop()" style="background:transparent;border:none;color:#555;font-size:18px;cursor:pointer">✕</button>
      </div>
      <div style="font-size:12px;color:#666;margin-bottom:14px">Питомец сопровождает тебя в бою — даёт пассивный баф и атакует врагов!</div>
      <div id="pet-current" style="margin-bottom:12px"></div>
      <div id="pet-list"></div>
    </div>
  </div>

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
  forest:        {icon:'🌲',name:'Тёмный Лес',          desc:'Волки, гоблины и разбойники',       reqLv:1,  enemies:['wolf','goblin','bandit'],           bg:'bg-forest',  mapX:68,  mapY:200, mapLoc:'village'},
  cave:          {icon:'🕳',name:'Пещера Ужаса',         desc:'Скелеты, пауки, летучие мыши',      reqLv:3,  enemies:['skeleton','spider','bat'],          bg:'bg-cave',    mapX:800, mapY:200, mapLoc:'village'},
  ruins:         {icon:'🏛',name:'Древние Руины',        desc:'Зомби, голем, тёмный маг',          reqLv:7,  enemies:['zombie','golem','darkmage'],        bg:'bg-ruins',   mapX:430, mapY:130, mapLoc:'village'},
  volcano:       {icon:'🌋',name:'Огненная Гора',        desc:'Огненный элементаль, дракончик',    reqLv:12, enemies:['fire_elem','dragonling','lava_troll'],bg:'bg-volcano', mapX:680, mapY:120, mapLoc:'village'},
  abyss:         {icon:'🌀',name:'Бездна',               desc:'Демоны, лич, теневой рыцарь',       reqLv:20, enemies:['demon','lich','shadow_knight'],     bg:'bg-abyss',   mapX:185, mapY:122, mapLoc:'village'},
  mountains:     {icon:'🏔',name:'Горное подземелье',    desc:'Ледяные тролли, снежные волки',     reqLv:10, enemies:['ice_troll','snow_wolf','harpy'],    bg:'bg-cave',    mapX:430, mapY:310, mapLoc:'mountains'},
  mountains_boss:{icon:'💀',name:'Логово Горного Босса', desc:'Каменный Дракон, ледяные стражи',   reqLv:15, enemies:['stone_drake','ice_guardian','frost_mage'],bg:'bg-abyss',mapX:680, mapY:280, mapLoc:'mountains'},
};
var ENEMIES={
  wolf:         {name:'Волк',            icon:'🐺',hp:30, atk:8, def:2, xp:15,gold:[1,5],  pool:'pf_common',   sprite:'wolf'},
  goblin:       {name:'Гоблин',          icon:'👺',hp:40, atk:10,def:3, xp:20,gold:[2,8],  pool:'pf_uncommon', sprite:'goblin'},
  bandit:       {name:'Разбойник',       icon:'🗡',hp:55, atk:13,def:4, xp:30,gold:[5,15], pool:'pf_uncommon', sprite:'bandit'},
  skeleton:     {name:'Скелет',          icon:'💀',hp:65, atk:14,def:5, xp:40,gold:[3,12], pool:'pc_common',   sprite:'skeleton'},
  spider:       {name:'Паук',            icon:'🕷',hp:50, atk:16,def:3, xp:35,gold:[2,8],  pool:'pc_common',   sprite:'spider'},
  bat:          {name:'Летучая мышь',    icon:'🦇',hp:35, atk:12,def:2, xp:25,gold:[1,6],  pool:'pc_common',   sprite:'bat'},
  zombie:       {name:'Зомби',           icon:'🧟',hp:90, atk:18,def:8, xp:60,gold:[8,20], pool:'pr_common',   sprite:'zombie'},
  golem:        {name:'Голем',           icon:'🗿',hp:130,atk:22,def:14,xp:90,gold:[12,30],pool:'pr_rare',     sprite:'golem'},
  darkmage:     {name:'Тёмный Маг',      icon:'🧙',hp:80, atk:28,def:6, xp:100,gold:[15,40],pool:'pr_rare',   sprite:'darkmage'},
  fire_elem:    {name:'Огн. Элем.',      icon:'🔥',hp:150,atk:30,def:10,xp:130,gold:[20,50],pool:'pv_uncommon',sprite:'fire_elem'},
  dragonling:   {name:'Дракончик',       icon:'🐉',hp:180,atk:35,def:12,xp:180,gold:[30,70],pool:'pv_rare',   sprite:'dragonling'},
  lava_troll:   {name:'Лавовый Тролль',  icon:'👹',hp:200,atk:28,def:18,xp:160,gold:[25,60],pool:'pv_uncommon',sprite:'lava_troll'},
  demon:        {name:'Демон',           icon:'😈',hp:250,atk:45,def:15,xp:250,gold:[50,100],pool:'pa_rare',  sprite:'demon'},
  lich:         {name:'Лич',             icon:'☠', hp:220,atk:50,def:10,xp:300,gold:[60,120],pool:'pa_epic',  sprite:'lich'},
  shadow_knight:{name:'Теневой Рыцарь',  icon:'🖤',hp:300,atk:40,def:25,xp:280,gold:[70,150],pool:'pa_epic', sprite:'shadow_knight'},
  ice_troll:    {name:'Ледяной Тролль',  icon:'🧊',hp:180,atk:28,def:16,xp:120,gold:[18,45], pool:'pm_common',sprite:'ice_troll'},
  snow_wolf:    {name:'Снежный Волк',    icon:'🐺',hp:100,atk:24,def:8,  xp:80, gold:[10,28], pool:'pm_common',sprite:'wolf'},
  harpy:        {name:'Гарпия',          icon:'🦅',hp:120,atk:32,def:6,  xp:100,gold:[14,35], pool:'pm_rare',  sprite:'harpy'},
  stone_drake:  {name:'Каменный Дракон', icon:'🐲',hp:280,atk:45,def:22,xp:220,gold:[40,90], pool:'pm_rare',  sprite:'dragonling'},
  ice_guardian: {name:'Ледяной Страж',   icon:'🛡',hp:250,atk:35,def:30,xp:200,gold:[35,80], pool:'pm_common',sprite:'golem'},
  frost_mage:   {name:'Ледяной Маг',     icon:'❄', hp:160,atk:50,def:8,  xp:180,gold:[30,70], pool:'pm_rare',  sprite:'darkmage'},
};

// SVG Sprites for monsters — drawn inline in battle
var MONSTER_SPRITES={
  wolf:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="40" cy="52" rx="22" ry="14" fill="#3a3a4a"/>
    <ellipse cx="40" cy="35" rx="16" ry="14" fill="#4a4a5a"/>
    <polygon points="30,24 26,10 34,22" fill="#4a4a5a"/><polygon points="50,24 54,10 46,22" fill="#4a4a5a"/>
    <circle cx="34" cy="33" r="3" fill="#111"/><circle cx="46" cy="33" r="3" fill="#111"/>
    <circle cx="35" cy="32" r="1" fill="#e8e8ff" opacity=".8"/><circle cx="47" cy="32" r="1" fill="#e8e8ff" opacity=".8"/>
    <ellipse cx="40" cy="42" rx="6" ry="4" fill="#5a3a3a"/>
    <rect x="24" y="55" width="6" height="14" rx="3" fill="#3a3a4a"/>
    <rect x="34" y="57" width="6" height="12" rx="3" fill="#3a3a4a"/>
    <rect x="44" y="57" width="6" height="12" rx="3" fill="#3a3a4a"/>
    <rect x="52" y="55" width="6" height="14" rx="3" fill="#3a3a4a"/>
    <path d="M55 35 Q65 32 68 28" stroke="#4a4a5a" stroke-width="3" fill="none" stroke-linecap="round"/>
    <circle cx="36" cy="40" r="1.5" fill="#ffaaaa" opacity=".6"/>
    <circle cx="44" cy="40" r="1.5" fill="#ffaaaa" opacity=".6"/>
  </svg>`,
  goblin:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="40" cy="55" rx="14" ry="18" fill="#2d6b2d"/>
    <ellipse cx="40" cy="32" rx="14" ry="13" fill="#3d8b3d"/>
    <polygon points="30,22 26,8 36,20" fill="#3d8b3d"/><polygon points="50,22 54,8 44,20" fill="#3d8b3d"/>
    <circle cx="35" cy="30" r="4" fill="#ffcc00"/><circle cx="45" cy="30" r="4" fill="#ffcc00"/>
    <circle cx="35" cy="30" r="2" fill="#111"/><circle cx="45" cy="30" r="2" fill="#111"/>
    <path d="M34 39 Q40 43 46 39" stroke="#1a4a1a" stroke-width="2" fill="none"/>
    <rect x="36" y="37" width="3" height="5" rx="1" fill="#aaa"/><rect x="41" y="37" width="3" height="5" rx="1" fill="#aaa"/>
    <rect x="28" y="58" width="7" height="15" rx="3" fill="#2d6b2d"/>
    <rect x="45" y="58" width="7" height="15" rx="3" fill="#2d6b2d"/>
    <line x1="20" y1="48" x2="28" y2="55" stroke="#2d6b2d" stroke-width="5" stroke-linecap="round"/>
    <line x1="60" y1="48" x2="52" y2="55" stroke="#2d6b2d" stroke-width="5" stroke-linecap="round"/>
    <circle cx="26" cy="46" r="4" fill="#3d8b3d"/>
    <circle cx="54" cy="46" r="4" fill="#3d8b3d"/>
    <rect x="54" y="42" width="3" height="16" rx="1" fill="#8b5a1a"/>
    <polygon points="57,42 61,35 63,43" fill="#aaa"/>
  </svg>`,
  bandit:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <rect x="28" y="45" width="24" height="24" rx="4" fill="#1a1a2e"/>
    <ellipse cx="40" cy="30" rx="13" ry="13" fill="#c8956c"/>
    <rect x="30" y="20" width="20" height="10" rx="5" fill="#2a2a3e"/>
    <rect x="27" y="23" width="26" height="5" rx="2" fill="#3a3a5e"/>
    <circle cx="35" cy="32" r="2" fill="#333"/><circle cx="45" cy="32" r="2" fill="#333"/>
    <path d="M35 38 Q40 42 45 38" stroke="#a06040" stroke-width="2" fill="none"/>
    <rect x="27" y="58" width="8" height="16" rx="3" fill="#1a1a2e"/>
    <rect x="45" y="58" width="8" height="16" rx="3" fill="#1a1a2e"/>
    <line x1="18" y1="48" x2="28" y2="55" stroke="#1a1a2e" stroke-width="6" stroke-linecap="round"/>
    <circle cx="17" cy="46" r="5" fill="#2a2a3e"/>
    <line x1="62" y1="48" x2="52" y2="55" stroke="#1a1a2e" stroke-width="6" stroke-linecap="round"/>
    <circle cx="63" cy="46" r="5" fill="#2a2a3e"/>
    <rect x="63" y="38" width="3" height="20" rx="1" fill="#888"/>
    <polygon points="66,38 70,30 72,39" fill="#bbb"/>
  </svg>`,
  skeleton:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="40" cy="27" rx="12" ry="13" fill="#ddd8cc"/>
    <circle cx="35" cy="25" r="3.5" fill="#111"/><circle cx="45" cy="25" r="3.5" fill="#111"/>
    <ellipse cx="40" cy="34" rx="5" ry="4" fill="#ddd8cc"/>
    <path d="M34 34 Q36 38 40 37 Q44 38 46 34" stroke="#bbb" stroke-width="2" fill="none"/>
    <rect x="34" y="38" width="12" height="18" rx="3" fill="#d4cfc3"/>
    <line x1="36" y1="38" x2="36" y2="56" stroke="#bbb" stroke-width="1"/>
    <line x1="40" y1="38" x2="40" y2="56" stroke="#bbb" stroke-width="1"/>
    <line x1="44" y1="38" x2="44" y2="56" stroke="#bbb" stroke-width="1"/>
    <rect x="31" y="58" width="7" height="16" rx="2" fill="#d4cfc3"/>
    <rect x="42" y="58" width="7" height="16" rx="2" fill="#d4cfc3"/>
    <line x1="18" y1="42" x2="34" y2="48" stroke="#d4cfc3" stroke-width="4" stroke-linecap="round"/>
    <line x1="62" y1="42" x2="46" y2="48" stroke="#d4cfc3" stroke-width="4" stroke-linecap="round"/>
    <circle cx="17" cy="40" r="5" fill="#d4cfc3"/>
    <circle cx="63" cy="40" r="5" fill="#d4cfc3"/>
    <line x1="63" y1="35" x2="63" y2="20" stroke="#ccc" stroke-width="2"/>
    <polygon points="60,20 63,12 66,20" fill="#ccc"/>
  </svg>`,
  spider:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="40" cy="48" rx="16" ry="12" fill="#1a0a1a"/>
    <ellipse cx="40" cy="34" rx="11" ry="9" fill="#2a0a2a"/>
    <circle cx="34" cy="31" r="3" fill="#ff0000" opacity=".8"/><circle cx="40" cy="30" r="2" fill="#ff0000" opacity=".6"/>
    <circle cx="46" cy="31" r="3" fill="#ff0000" opacity=".8"/>
    <line x1="18" y1="38" x2="30" y2="44" stroke="#1a0a1a" stroke-width="3" stroke-linecap="round"/>
    <line x1="14" y1="44" x2="28" y2="48" stroke="#1a0a1a" stroke-width="3" stroke-linecap="round"/>
    <line x1="16" y1="52" x2="28" y2="52" stroke="#1a0a1a" stroke-width="3" stroke-linecap="round"/>
    <line x1="62" y1="38" x2="50" y2="44" stroke="#1a0a1a" stroke-width="3" stroke-linecap="round"/>
    <line x1="66" y1="44" x2="52" y2="48" stroke="#1a0a1a" stroke-width="3" stroke-linecap="round"/>
    <line x1="64" y1="52" x2="52" y2="52" stroke="#1a0a1a" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="20" x2="40" y2="8" stroke="#888" stroke-width="1.5" stroke-dasharray="3,2"/>
    <path d="M33 50 Q40 56 47 50" stroke="#3a0a3a" stroke-width="2" fill="none"/>
  </svg>`,
  bat:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <path d="M40 40 Q25 30 10 35 Q18 28 30 32 Q40 25 50 32 Q62 28 70 35 Q55 30 40 40Z" fill="#2a1a3a"/>
    <ellipse cx="40" cy="44" rx="9" ry="8" fill="#3a2a4a"/>
    <circle cx="37" cy="41" r="3" fill="#ff4444" opacity=".9"/><circle cx="43" cy="41" r="3" fill="#ff4444" opacity=".9"/>
    <circle cx="37" cy="41" r="1.5" fill="#111"/><circle cx="43" cy="41" r="1.5" fill="#111"/>
    <path d="M36 48 Q40 52 44 48" stroke="#2a1a3a" stroke-width="1.5" fill="none"/>
    <polygon points="37,50 36,55 38,52"/><polygon points="43,50 44,55 42,52" fill="#2a1a3a"/>
    <polygon points="35,36 33,30 37,34" fill="#3a2a4a"/>
    <polygon points="45,36 47,30 43,34" fill="#3a2a4a"/>
  </svg>`,
  zombie:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <rect x="28" y="44" width="24" height="24" rx="3" fill="#2a4a2a"/>
    <ellipse cx="40" cy="30" rx="13" ry="13" fill="#5a7a4a"/>
    <circle cx="35" cy="28" r="3" fill="#ffff00" opacity=".8"/><circle cx="45" cy="28" r="3" fill="#ffff00" opacity=".8"/>
    <circle cx="35" cy="28" r="1.5" fill="#333"/><circle cx="45" cy="28" r="1.5" fill="#333"/>
    <path d="M34 37 Q37 40 40 38 Q43 40 46 37" stroke="#3a5a3a" stroke-width="2" fill="none"/>
    <line x1="36" y1="37" x2="35" y2="40" stroke="#4a6a4a" stroke-width="2"/>
    <line x1="44" y1="37" x2="45" y2="40" stroke="#4a6a4a" stroke-width="2"/>
    <rect x="28" y="58" width="9" height="16" rx="2" fill="#2a4a2a"/>
    <rect x="43" y="58" width="9" height="16" rx="2" fill="#2a4a2a"/>
    <line x1="18" y1="40" x2="28" y2="50" stroke="#2a4a2a" stroke-width="6" stroke-linecap="round"/>
    <line x1="55" y1="36" x2="52" y2="50" stroke="#2a4a2a" stroke-width="6" stroke-linecap="round"/>
    <circle cx="17" cy="38" r="5" fill="#3a5a3a"/>
    <circle cx="57" cy="34" r="5" fill="#3a5a3a"/>
    <path d="M25 22 Q30 18 35 22" stroke="#8aaa6a" stroke-width="1.5" fill="none" opacity=".6"/>
    <circle cx="33" cy="20" r="2" fill="#8aaa6a" opacity=".5"/>
  </svg>`,
  golem:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <rect x="26" y="42" width="28" height="30" rx="4" fill="#5a5a6a"/>
    <rect x="28" y="20" width="24" height="24" rx="6" fill="#6a6a7a"/>
    <rect x="30" y="22" width="8" height="8" rx="2" fill="#ff6600" opacity=".8"/>
    <rect x="42" y="22" width="8" height="8" rx="2" fill="#ff6600" opacity=".8"/>
    <rect x="30" y="22" width="8" height="8" rx="2" fill="#ffaa00" opacity=".5"/>
    <rect x="42" y="22" width="8" height="8" rx="2" fill="#ffaa00" opacity=".5"/>
    <path d="M33 34 Q40 38 47 34" stroke="#888" stroke-width="2" fill="none"/>
    <rect x="12" y="42" width="14" height="24" rx="5" fill="#5a5a6a"/>
    <rect x="54" y="42" width="14" height="24" rx="5" fill="#5a5a6a"/>
    <rect x="30" y="72" width="9" height="8" rx="2" fill="#5a5a6a"/>
    <rect x="41" y="72" width="9" height="8" rx="2" fill="#5a5a6a"/>
    <line x1="32" y1="26" x2="46" y2="26" stroke="#888" stroke-width="1" opacity=".5"/>
    <line x1="32" y1="30" x2="46" y2="30" stroke="#888" stroke-width="1" opacity=".5"/>
    <line x1="32" y1="46" x2="52" y2="46" stroke="#888" stroke-width="1" opacity=".4"/>
  </svg>`,
  darkmage:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="40" cy="56" rx="16" ry="20" fill="#1a0a2e"/>
    <ellipse cx="40" cy="28" rx="12" ry="13" fill="#c8956c"/>
    <path d="M28 22 Q30 8 40 10 Q50 8 52 22 Q46 18 40 20 Q34 18 28 22Z" fill="#1a0a2e"/>
    <polygon points="40,8 36,18 44,18" fill="#2a0a3e"/>
    <circle cx="35" cy="27" r="3" fill="#aa00ff" opacity=".9"/><circle cx="45" cy="27" r="3" fill="#aa00ff" opacity=".9"/>
    <path d="M35 34 Q40 37 45 34" stroke="#a06040" stroke-width="2" fill="none"/>
    <line x1="18" y1="46" x2="28" y2="54" stroke="#1a0a2e" stroke-width="5" stroke-linecap="round"/>
    <circle cx="16" cy="44" r="5" fill="#2a0a3e"/>
    <line x1="62" y1="46" x2="52" y2="54" stroke="#1a0a2e" stroke-width="5" stroke-linecap="round"/>
    <circle cx="64" cy="44" r="5" fill="#2a0a3e"/>
    <line x1="64" y1="38" x2="64" y2="18" stroke="#6a2a8a" stroke-width="3" stroke-linecap="round"/>
    <circle cx="64" cy="16" r="7" fill="#aa44ff" opacity=".8"/>
    <circle cx="64" cy="16" r="4" fill="#ffffff" opacity=".6"/>
    <circle cx="56" cy="12" r="3" fill="#aa44ff" opacity=".5"/>
    <circle cx="72" cy="12" r="3" fill="#aa44ff" opacity=".5"/>
  </svg>`,
  fire_elem:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <defs><radialGradient id="fg1" cx="50%" cy="80%" r="60%"><stop offset="0%" stop-color="#ff8c00"/><stop offset="100%" stop-color="#ff2200" stop-opacity="0"/></radialGradient></defs>
    <ellipse cx="40" cy="55" rx="18" ry="10" fill="url(#fg1)" opacity=".6"/>
    <path d="M40 70 Q28 60 26 46 Q24 34 32 26 Q30 38 36 40 Q32 30 38 18 Q40 30 44 28 Q46 20 44 12 Q52 22 50 34 Q56 28 54 18 Q62 28 58 44 Q56 56 52 62 Q48 68 40 70Z" fill="#ff4400"/>
    <path d="M40 65 Q32 56 30 46 Q28 36 34 30 Q33 40 38 42 Q36 34 40 24 Q42 34 46 32 Q50 26 48 18 Q56 28 52 42 Q55 52 50 60 Q46 66 40 65Z" fill="#ff8800"/>
    <path d="M40 60 Q34 52 34 44 Q34 36 38 32 Q38 42 41 44 Q43 36 40 28 Q46 36 46 44 Q46 54 40 60Z" fill="#ffcc00"/>
    <circle cx="36" cy="44" r="4" fill="#fff" opacity=".3"/>
    <circle cx="44" cy="44" r="4" fill="#fff" opacity=".3"/>
  </svg>`,
  dragonling:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="40" cy="52" rx="20" ry="14" fill="#2a5a1a"/>
    <ellipse cx="40" cy="30" rx="15" ry="14" fill="#3a7a2a"/>
    <path d="M28 22 Q22 10 28 16 Q32 8 34 16" stroke="#3a7a2a" stroke-width="3" fill="none"/>
    <path d="M52 22 Q58 10 52 16 Q48 8 46 16" stroke="#3a7a2a" stroke-width="3" fill="none"/>
    <circle cx="35" cy="28" r="4" fill="#ffcc00"/><circle cx="45" cy="28" r="4" fill="#ffcc00"/>
    <circle cx="35" cy="28" r="2" fill="#111"/><circle cx="45" cy="28" r="2" fill="#111"/>
    <path d="M34 38 Q40 44 46 38" stroke="#2a5a1a" stroke-width="2" fill="none"/>
    <path d="M46 38 Q50 42 52 40 Q54 36 56 38" stroke="#ff4400" stroke-width="2" fill="none"/>
    <rect x="29" y="55" width="8" height="16" rx="3" fill="#2a5a1a"/>
    <rect x="43" y="55" width="8" height="16" rx="3" fill="#2a5a1a"/>
    <path d="M52 48 Q62 40 68 42 Q65 50 58 52 Q60 58 55 55Z" fill="#3a7a2a"/>
    <path d="M28 48 Q18 40 12 42 Q15 50 22 52 Q20 58 25 55Z" fill="#3a7a2a"/>
    <path d="M56 60 Q64 65 70 72" stroke="#2a5a1a" stroke-width="4" stroke-linecap="round"/>
  </svg>`,
  lava_troll:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <rect x="24" y="44" width="32" height="28" rx="5" fill="#3a2010"/>
    <ellipse cx="40" cy="28" rx="18" ry="16" fill="#4a2a14"/>
    <circle cx="34" cy="26" r="4" fill="#ff4400" opacity=".9"/><circle cx="46" cy="26" r="4" fill="#ff4400" opacity=".9"/>
    <circle cx="34" cy="26" r="2" fill="#ffcc00"/><circle cx="46" cy="26" r="2" fill="#ffcc00"/>
    <path d="M32 36 Q40 42 48 36" stroke="#ff4400" stroke-width="2" fill="none"/>
    <rect x="37" y="36" width="4" height="7" rx="1" fill="#ff6600"/>
    <rect x="10" y="44" width="14" height="26" rx="5" fill="#3a2010"/>
    <rect x="56" y="44" width="14" height="26" rx="5" fill="#3a2010"/>
    <rect x="28" y="72" width="10" height="8" rx="2" fill="#3a2010"/>
    <rect x="42" y="72" width="10" height="8" rx="2" fill="#3a2010"/>
    <path d="M30 18 Q28 10 34 14" stroke="#ff6600" stroke-width="2" fill="none" opacity=".7"/>
    <path d="M50 18 Q52 10 46 14" stroke="#ff6600" stroke-width="2" fill="none" opacity=".7"/>
    <ellipse cx="40" cy="46" rx="12" ry="4" fill="#ff4400" opacity=".2"/>
  </svg>`,
  demon:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="40" cy="55" rx="18" ry="20" fill="#3a0a0a"/>
    <ellipse cx="40" cy="28" rx="15" ry="14" fill="#5a1010"/>
    <polygon points="30,18 25,5 33,16" fill="#5a1010"/><polygon points="50,18 55,5 47,16" fill="#5a1010"/>
    <circle cx="35" cy="26" r="4" fill="#ff0000"/><circle cx="45" cy="26" r="4" fill="#ff0000"/>
    <circle cx="35" cy="26" r="2" fill="#ffcc00"/><circle cx="45" cy="26" r="2" fill="#ffcc00"/>
    <path d="M33 36 Q40 42 47 36" stroke="#8a0000" stroke-width="2" fill="none"/>
    <rect x="37" y="36" width="3" height="6" rx="1" fill="#ff4444"/>
    <rect x="41" y="36" width="3" height="6" rx="1" fill="#ff4444"/>
    <path d="M22 46 Q12 36 10 28 Q16 30 20 38 Q24 44 26 46Z" fill="#3a0a0a"/>
    <path d="M58 46 Q68 36 70 28 Q64 30 60 38 Q56 44 54 46Z" fill="#3a0a0a"/>
    <rect x="25" y="62" width="10" height="14" rx="4" fill="#3a0a0a"/>
    <rect x="45" y="62" width="10" height="14" rx="4" fill="#3a0a0a"/>
    <path d="M40 72 Q32 78 28 72" stroke="#5a1010" stroke-width="2" fill="none"/>
    <ellipse cx="40" cy="55" rx="8" ry="4" fill="#ff0000" opacity=".15"/>
  </svg>`,
  lich:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="40" cy="56" rx="15" ry="20" fill="#0a0a1a"/>
    <ellipse cx="40" cy="27" rx="12" ry="13" fill="#c8c8d8"/>
    <circle cx="35" cy="24" r="4" fill="#aa00ff" opacity=".9"/><circle cx="45" cy="24" r="4" fill="#aa00ff" opacity=".9"/>
    <circle cx="35" cy="24" r="2" fill="#fff" opacity=".8"/><circle cx="45" cy="24" r="2" fill="#fff" opacity=".8"/>
    <ellipse cx="40" cy="33" rx="5" ry="4" fill="#c8c8d8"/>
    <path d="M35 33 Q38 37 40 36 Q42 37 45 33" stroke="#aaa" stroke-width="1.5" fill="none"/>
    <path d="M28 22 Q30 8 40 10 Q50 8 52 22" fill="#0a0a1a" stroke="#2a0a4a" stroke-width="1"/>
    <line x1="16" y1="46" x2="28" y2="54" stroke="#0a0a1a" stroke-width="5" stroke-linecap="round"/>
    <circle cx="14" cy="44" r="5" fill="#1a0a2a"/>
    <line x1="64" y1="46" x2="52" y2="54" stroke="#0a0a1a" stroke-width="5" stroke-linecap="round"/>
    <circle cx="66" cy="44" r="5" fill="#1a0a2a"/>
    <line x1="14" y1="38" x2="14" y2="18" stroke="#6a2aaa" stroke-width="3"/>
    <circle cx="14" cy="15" r="8" fill="#aa00ff" opacity=".7"/>
    <circle cx="14" cy="15" r="5" fill="#cc44ff" opacity=".8"/>
    <circle cx="14" cy="15" r="2" fill="#fff" opacity=".9"/>
    <circle cx="40" cy="12" r="10" fill="#0a0a1a" opacity=".4"/>
    <text x="40" y="17" text-anchor="middle" font-size="12" fill="#aa00ff" opacity=".8">☠</text>
  </svg>`,
  shadow_knight:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <rect x="26" y="42" width="28" height="28" rx="3" fill="#0a0a14"/>
    <rect x="28" y="44" width="24" height="24" rx="2" fill="#14142a" stroke="#3a3a6a" stroke-width="1"/>
    <rect x="28" y="18" width="24" height="26" rx="6" fill="#1a1a2e" stroke="#3a3a6a" stroke-width="1.5"/>
    <rect x="30" y="20" width="20" height="12" rx="4" fill="#0a0a18"/>
    <circle cx="35" cy="26" r="4" fill="#4444ff" opacity=".8"/><circle cx="45" cy="26" r="4" fill="#4444ff" opacity=".8"/>
    <circle cx="35" cy="26" r="2" fill="#aaaaff"/><circle cx="45" cy="26" r="2" fill="#aaaaff"/>
    <rect x="10" y="42" width="16" height="26" rx="4" fill="#0a0a14" stroke="#3a3a6a" stroke-width="1"/>
    <rect x="54" y="42" width="16" height="26" rx="4" fill="#0a0a14" stroke="#3a3a6a" stroke-width="1"/>
    <rect x="28" y="70" width="10" height="10" rx="2" fill="#0a0a14"/>
    <rect x="42" y="70" width="10" height="10" rx="2" fill="#0a0a14"/>
    <rect x="62" y="32" width="4" height="36" rx="2" fill="#888" stroke="#aaa" stroke-width="0.5"/>
    <polygon points="62,32 66,22 70,32" fill="#aaa"/>
    <rect x="57" y="44" width="14" height="3" rx="1" fill="#666"/>
    <ellipse cx="40" cy="56" rx="14" ry="4" fill="#4444ff" opacity=".08"/>
  </svg>`,
  ice_troll:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <rect x="24" y="44" width="32" height="28" rx="5" fill="#2a4a6a"/>
    <ellipse cx="40" cy="28" rx="18" ry="16" fill="#3a6a8a"/>
    <circle cx="34" cy="26" r="4" fill="#aaeeff"/><circle cx="46" cy="26" r="4" fill="#aaeeff"/>
    <circle cx="34" cy="26" r="2" fill="#001133"/><circle cx="46" cy="26" r="2" fill="#001133"/>
    <path d="M32 36 Q40 42 48 36" stroke="#2a4a6a" stroke-width="2" fill="none"/>
    <rect x="37" y="36" width="4" height="7" rx="1" fill="#88ccff"/>
    <rect x="10" y="44" width="14" height="26" rx="5" fill="#2a4a6a"/>
    <rect x="56" y="44" width="14" height="26" rx="5" fill="#2a4a6a"/>
    <rect x="28" y="72" width="10" height="8" rx="2" fill="#2a4a6a"/>
    <rect x="42" y="72" width="10" height="8" rx="2" fill="#2a4a6a"/>
    <polygon points="30,16 32,8 34,16" fill="#aaeeff" opacity=".8"/>
    <polygon points="40,14 42,6 44,14" fill="#aaeeff" opacity=".8"/>
    <polygon points="46,16 48,8 50,16" fill="#aaeeff" opacity=".8"/>
    <ellipse cx="40" cy="50" rx="12" ry="4" fill="#88ccff" opacity=".2"/>
  </svg>`,
  harpy:`<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
    <ellipse cx="40" cy="50" rx="12" ry="16" fill="#4a3a1a"/>
    <ellipse cx="40" cy="28" rx="11" ry="11" fill="#c8956c"/>
    <circle cx="35" cy="26" r="3" fill="#ff8800"/><circle cx="45" cy="26" r="3" fill="#ff8800"/>
    <circle cx="35" cy="26" r="1.5" fill="#111"/><circle cx="45" cy="26" r="1.5" fill="#111"/>
    <path d="M36 34 Q40 38 44 34" stroke="#a06040" stroke-width="2" fill="none"/>
    <path d="M16 38 Q10 28 14 20 Q20 26 22 34 Q24 38 28 42Z" fill="#5a4a2a"/>
    <path d="M64 38 Q70 28 66 20 Q60 26 58 34 Q56 38 52 42Z" fill="#5a4a2a"/>
    <path d="M16 38 Q10 28 14 20 Q20 26 22 34" stroke="#7a6a3a" stroke-width="1" fill="none"/>
    <path d="M64 38 Q70 28 66 20 Q60 26 58 34" stroke="#7a6a3a" stroke-width="1" fill="none"/>
    <rect x="34" y="60" width="6" height="14" rx="2" fill="#4a3a1a"/>
    <rect x="34" y="60" width="3" height="6" rx="1" fill="#8a6a2a"/>
    <rect x="43" y="60" width="3" height="6" rx="1" fill="#8a6a2a"/>
    <polygon points="40,18 38,10 42,10" fill="#ff8800"/>
  </svg>`,
};

// BOSSES (world bosses, separate from dungeon)
var WORLD_BOSSES={
  forest_boss:{name:'Лесной Король',    icon:'🌿',sprite:'forest_king',  hp:2000, atk:40,def:15,xp:800, gold:[200,400], pool:'pf_uncommon',
    desc:'Древний дух леса. Повелевает зверями.'},
  cave_boss:  {name:'Горный Дракон',    icon:'🐲',sprite:'dragonling',   hp:5000, atk:60,def:20,xp:2000,gold:[500,900], pool:'pc_rare',
    desc:'Страж подземелья. Дышит ядом.'},
  ruins_boss: {name:'Некромант Руин',   icon:'☠', sprite:'lich',         hp:4000, atk:55,def:12,xp:1500,gold:[400,700], pool:'pr_rare',
    desc:'Поднимает павших воинов.'},
  volcano_boss:{name:'Огненный Титан',  icon:'🔥',sprite:'fire_elem',    hp:8000, atk:80,def:25,xp:3000,gold:[800,1400],pool:'pv_rare',
    desc:'Рождён в жерле вулкана.'},
  abyss_boss: {name:'Повелитель Бездны',icon:'👿',sprite:'demon',        hp:15000,atk:120,def:35,xp:6000,gold:[2000,3500],pool:'pa_epic',
    desc:'Источник тёмной магии.'},
};


// ITEMS — 8 SLOT TYPES
var SLOT_ICONS={weapon:'⚔',armor:'🛡',helmet:'⛑',ring:'💍',gloves:'🧤',pants:'👖',boots:'👢',amulet:'📿'};
var RARITY_LABEL={common:'Обычный',uncommon:'Необычный',rare:'Редкий',epic:'Эпический',legendary:'Легендарный',mythic:'МИФИЧЕСКИЙ'};
var ITEMS={
  // ── COMMON ──────────────────────────────────────────────────────
  worn_sword:      {n:'Ржавый Меч',           i:'🗡', t:'weapon', r:'common',   atk:3,  def:0,  hp:0,   crit:0,  desc:'Старый, но острый',                sell:5},
  bone_dagger:     {n:'Костяной Кинжал',      i:'🦴', t:'weapon', r:'common',   atk:5,  def:0,  hp:0,   crit:3,  desc:'Сделан из кости монстра',          sell:6},
  wooden_club:     {n:'Деревянная Дубина',    i:'🪵', t:'weapon', r:'common',   atk:4,  def:1,  hp:5,   crit:0,  desc:'Грубо, но больно',                 sell:4},
  leather_gloves:  {n:'Кожаные Перч.',        i:'🧤', t:'gloves', r:'common',   atk:0,  def:2,  hp:10,  crit:1,  desc:'Простая защита',                   sell:4},
  iron_ring:       {n:'Железное Кольцо',      i:'💍', t:'ring',   r:'common',   atk:1,  def:1,  hp:5,   crit:0,  desc:'Грубая работа',                    sell:3},
  cave_ring:       {n:'Пещерное Кольцо',      i:'💍', t:'ring',   r:'common',   atk:2,  def:0,  hp:8,   crit:2,  desc:'Найдено в пещере',                 sell:5},
  iron_helmet:     {n:'Железный Шлем',        i:'⛑', t:'helmet', r:'common',   atk:0,  def:3,  hp:15,  crit:0,  desc:'Надёжная защита',                  sell:8},
  cloth_boots:     {n:'Тряпичные Сапоги',     i:'👢', t:'boots',  r:'common',   atk:0,  def:1,  hp:8,   crit:0,  desc:'Хоть что-то на ногах',             sell:3},
  tattered_pants:  {n:'Рваные Штаны',         i:'👖', t:'pants',  r:'common',   atk:0,  def:2,  hp:10,  crit:0,  desc:'Видали лучшие дни',                sell:3},
  copper_amulet:   {n:'Медный Амулет',        i:'📿', t:'amulet', r:'common',   atk:1,  def:1,  hp:8,   crit:1,  desc:'Дешёвый оберег',                   sell:4},
  // ── UNCOMMON ────────────────────────────────────────────────────
  hunters_bow:     {n:'Охотничий Лук',        i:'🏹', t:'weapon', r:'uncommon', atk:8,  def:0,  hp:0,   crit:5,  desc:'Точный и быстрый',                 sell:15},
  steel_sword:     {n:'Стальной Меч',         i:'⚔', t:'weapon', r:'uncommon', atk:12, def:1,  hp:0,   crit:4,  desc:'Хорошая сталь',                    sell:25},
  iron_spear:      {n:'Железное Копьё',       i:'🔱', t:'weapon', r:'uncommon', atk:10, def:2,  hp:0,   crit:3,  desc:'Длинный охват',                    sell:20},
  leather_armor:   {n:'Кожаная Броня',        i:'🦺', t:'armor',  r:'uncommon', atk:0,  def:6,  hp:25,  crit:0,  desc:'Лёгкая и прочная',                 sell:20},
  chain_armor:     {n:'Кольчуга',             i:'🛡', t:'armor',  r:'uncommon', atk:0,  def:8,  hp:20,  crit:0,  desc:'Гибкая стальная защита',           sell:28},
  silver_ring:     {n:'Серебряное Кольцо',    i:'💍', t:'ring',   r:'uncommon', atk:3,  def:2,  hp:15,  crit:2,  desc:'Очищает проклятия',                sell:18},
  chain_pants:     {n:'Кольчужные Штаны',     i:'👖', t:'pants',  r:'uncommon', atk:0,  def:7,  hp:20,  crit:0,  desc:'Звенят при ходьбе',                sell:22},
  shadow_hood:     {n:'Капюшон Теней',        i:'🎭', t:'helmet', r:'uncommon', atk:2,  def:4,  hp:20,  crit:3,  desc:'Растворяешься в тени',             sell:30},
  druid_amulet:    {n:'Амулет Друида',        i:'📿', t:'amulet', r:'uncommon', atk:2,  def:2,  hp:20,  crit:2,  desc:'Связь с природой',                 sell:28},
  battle_gloves:   {n:'Боевые Перчатки',      i:'🧤', t:'gloves', r:'uncommon', atk:4,  def:3,  hp:15,  crit:3,  desc:'Усиливают удар',                   sell:26},
  ranger_boots:    {n:'Сапоги Следопыта',     i:'👢', t:'boots',  r:'uncommon', atk:2,  def:4,  hp:18,  crit:2,  desc:'Бесшумны в лесу',                  sell:24},
  scout_ring:      {n:'Кольцо Разведчика',    i:'💍', t:'ring',   r:'uncommon', atk:2,  def:3,  hp:12,  crit:3,  desc:'Обостряет чувства',                sell:20},
  // ── RARE ────────────────────────────────────────────────────────
  elven_blade:     {n:'Эльфийский Клинок',    i:'🌿', t:'weapon', r:'rare',     atk:18, def:2,  hp:10,  crit:7,  desc:'Выкован из лунного серебра',       sell:80},
  cursed_blade:    {n:'Проклятый Клинок',     i:'🖤', t:'weapon', r:'rare',     atk:22, def:0,  hp:-10, crit:8,  desc:'Сила требует жертв',               sell:90},
  arcane_staff:    {n:'Арканный Посох',       i:'🪄', t:'weapon', r:'rare',     atk:20, def:3,  hp:20,  crit:5,  desc:'Усиливает заклинания',             sell:100},
  frost_axe:       {n:'Ледяной Топор',        i:'🪓', t:'weapon', r:'rare',     atk:24, def:1,  hp:0,   crit:6,  desc:'Замораживает врагов',              sell:95},
  thunder_wand:    {n:'Жезл Грома',           i:'⚡', t:'weapon', r:'rare',     atk:19, def:4,  hp:15,  crit:6,  desc:'Бьёт молнией',                     sell:105},
  forest_cloak:    {n:'Лесной Плащ',          i:'🍃', t:'armor',  r:'rare',     atk:1,  def:12, hp:40,  crit:3,  desc:'Шуршит листьями',                  sell:70},
  plate_armor:     {n:'Латные Доспехи',       i:'🛡', t:'armor',  r:'rare',     atk:0,  def:18, hp:50,  crit:0,  desc:'Тяжёлая броня воина',              sell:110},
  runic_armor:     {n:'Руническая Броня',     i:'🛡', t:'armor',  r:'rare',     atk:3,  def:15, hp:45,  crit:2,  desc:'Покрыта защитными рунами',         sell:120},
  mana_ring:       {n:'Кольцо Маны',          i:'🔮', t:'ring',   r:'rare',     atk:5,  def:3,  hp:30,  crit:4,  desc:'Пульсирует магией',                sell:65},
  guardian_ring:   {n:'Кольцо Стража',        i:'💍', t:'ring',   r:'rare',     atk:4,  def:6,  hp:25,  crit:3,  desc:'Защищает от тьмы',                 sell:75},
  blood_ring:      {n:'Кольцо Крови',         i:'💍', t:'ring',   r:'rare',     atk:7,  def:1,  hp:20,  crit:5,  desc:'Питается кровью',                  sell:85},
  rune_helmet:     {n:'Рунный Шлем',          i:'⛑', t:'helmet', r:'rare',     atk:3,  def:10, hp:40,  crit:4,  desc:'Покрыт рунами защиты',             sell:85},
  war_helmet:      {n:'Боевой Шлем',          i:'⛑', t:'helmet', r:'rare',     atk:2,  def:13, hp:35,  crit:2,  desc:'Украшен гребнем',                  sell:90},
  arcane_amulet:   {n:'Аркановый Амулет',     i:'📿', t:'amulet', r:'rare',     atk:6,  def:4,  hp:35,  crit:5,  desc:'Пульсирует тёмной магией',         sell:90},
  nature_amulet:   {n:'Амулет Природы',       i:'🌿', t:'amulet', r:'rare',     atk:3,  def:6,  hp:40,  crit:3,  desc:'Дар лесных духов',                 sell:80},
  battle_pants:    {n:'Латные Штаны',         i:'👖', t:'pants',  r:'rare',     atk:2,  def:12, hp:35,  crit:2,  desc:'Прочная защита',                   sell:80},
  wind_pants:      {n:'Штаны Ветра',          i:'👖', t:'pants',  r:'rare',     atk:4,  def:9,  hp:30,  crit:4,  desc:'Лёгкие и подвижные',               sell:85},
  iron_boots:      {n:'Железные Сапоги',      i:'👢', t:'boots',  r:'rare',     atk:0,  def:10, hp:28,  crit:1,  desc:'Тяжёлые, но надёжные',             sell:75},
  swift_boots:     {n:'Сапоги Быстроты',      i:'👢', t:'boots',  r:'rare',     atk:3,  def:7,  hp:20,  crit:4,  desc:'Ускоряют движение',                sell:80},
  warrior_gloves:  {n:'Латные Перчатки',      i:'🧤', t:'gloves', r:'rare',     atk:5,  def:6,  hp:20,  crit:3,  desc:'Стальные пластины',                sell:85},
  // ── EPIC ────────────────────────────────────────────────────────
  dragon_scale:    {n:'Чешуя Дракона',        i:'🐉', t:'armor',  r:'epic',     atk:5,  def:25, hp:70,  crit:4,  desc:'Огненная броня',                   sell:300},
  flame_sword:     {n:'Огненный Меч',         i:'🔥', t:'weapon', r:'epic',     atk:35, def:5,  hp:15,  crit:8,  desc:'Горит вечным пламенем',            sell:350},
  shadow_blade:    {n:'Клинок Теней',         i:'🌑', t:'weapon', r:'epic',     atk:45, def:3,  hp:10,  crit:10, desc:'Рубит саму тьму',                  sell:500},
  lich_staff:      {n:'Посох Лича',           i:'☠', t:'weapon', r:'epic',     atk:50, def:8,  hp:-20, crit:9,  desc:'Содержит душу лича',               sell:520},
  void_blade:      {n:'Клинок Пустоты',       i:'🌀', t:'weapon', r:'epic',     atk:42, def:6,  hp:0,   crit:11, desc:'Режет пространство',               sell:480},
  storm_hammer:    {n:'Молот Бури',           i:'🔨', t:'weapon', r:'epic',     atk:40, def:10, hp:30,  crit:6,  desc:'Удар грома',                       sell:460},
  dragon_helm:     {n:'Шлем Дракона',         i:'🐉', t:'helmet', r:'epic',     atk:8,  def:18, hp:60,  crit:5,  desc:'Дышит огнём',                      sell:280},
  soul_crown:      {n:'Корона Душ',           i:'👑', t:'helmet', r:'epic',     atk:12, def:15, hp:80,  crit:6,  desc:'Поглощает души врагов',            sell:400},
  shadow_mask:     {n:'Маска Теней',          i:'🎭', t:'helmet', r:'epic',     atk:10, def:12, hp:60,  crit:8,  desc:'Скрывает истинное лицо',           sell:350},
  void_armor:      {n:'Броня Пустоты',        i:'🌀', t:'armor',  r:'epic',     atk:8,  def:30, hp:60,  crit:3,  desc:'Из другого измерения',             sell:450},
  lava_armor:      {n:'Лавовые Латы',         i:'🌋', t:'armor',  r:'epic',     atk:10, def:28, hp:50,  crit:3,  desc:'Раскалены изнутри',                sell:420},
  death_ring:      {n:'Кольцо Смерти',        i:'💀', t:'ring',   r:'epic',     atk:15, def:10, hp:40,  crit:6,  desc:'Холодный как могила',              sell:380},
  phoenix_amulet:  {n:'Амулет Феникса',       i:'📿', t:'amulet', r:'epic',     atk:10, def:8,  hp:50,  crit:6,  desc:'Возрождает владельца',             sell:320},
  void_amulet:     {n:'Амулет Пустоты',       i:'📿', t:'amulet', r:'epic',     atk:12, def:12, hp:60,  crit:7,  desc:'Притягивает тёмную энергию',       sell:420},
  volcano_boots:   {n:'Сапоги Вулкана',       i:'👢', t:'boots',  r:'epic',     atk:5,  def:14, hp:40,  crit:4,  desc:'Оставляют следы огня',             sell:340},
  abyss_boots:     {n:'Сапоги Бездны',        i:'👢', t:'boots',  r:'epic',     atk:6,  def:18, hp:50,  crit:5,  desc:'Бесшумны как тьма',               sell:380},
  titan_boots:     {n:'Сапоги Титана',        i:'👢', t:'boots',  r:'epic',     atk:4,  def:20, hp:55,  crit:3,  desc:'Тяжёлые как скала',               sell:360},
  inferno_pants:   {n:'Штаны Инферно',        i:'👖', t:'pants',  r:'epic',     atk:8,  def:18, hp:50,  crit:4,  desc:'Горят, но не сгорают',             sell:360},
  shadow_pants:    {n:'Штаны Теней',          i:'👖', t:'pants',  r:'epic',     atk:10, def:14, hp:45,  crit:6,  desc:'Растворяются в темноте',           sell:370},
  war_gloves:      {n:'Перчатки Войны',       i:'🧤', t:'gloves', r:'epic',     atk:12, def:8,  hp:30,  crit:5,  desc:'Пробивают любую броню',            sell:340},
  // ── LEGENDARY ───────────────────────────────────────────────────
  inferno_blade:   {n:'Клинок Инферно',       i:'💥', t:'weapon', r:'legendary',atk:60, def:10, hp:20,  crit:12, desc:'Испепеляет всё живое',             sell:1500},
  legend_bow:      {n:'Лук Легенды',          i:'🏹', t:'weapon', r:'legendary',atk:55, def:5,  hp:30,  crit:15, desc:'Стрелы никогда не промахуются',    sell:1400},
  druid_staff:     {n:'Посох Друида',         i:'🌳', t:'weapon', r:'legendary',atk:48, def:15, hp:60,  crit:10, desc:'Голос леса',                       sell:1600},
  thunder_blade:   {n:'Громовой Клинок',      i:'⚡', t:'weapon', r:'legendary',atk:65, def:8,  hp:10,  crit:14, desc:'Бьёт молнией каждый удар',         sell:1650},
  soul_reaver:     {n:'Пожиратель Душ',       i:'🔱', t:'weapon', r:'legendary',atk:58, def:12, hp:-20, crit:16, desc:'Крадёт жизнь врага',               sell:1700},
  paladin_armor:   {n:'Броня Паладина',       i:'⚔', t:'armor',  r:'legendary',atk:10, def:40, hp:120, crit:5,  desc:'Священная защита',                 sell:2000},
  dragon_lord_helm:{n:'Шлем Повелителя Дракона',i:'🐲',t:'helmet',r:'legendary',atk:18,def:30, hp:100, crit:10, desc:'Командует драконами',               sell:1800},
  nature_ring:     {n:'Кольцо Природы',       i:'🌿', t:'ring',   r:'legendary',atk:20, def:20, hp:100, crit:8,  desc:'Гармония всего живого',            sell:1800},
  eternity_ring:   {n:'Кольцо Вечности',      i:'💍', t:'ring',   r:'legendary',atk:18, def:18, hp:90,  crit:10, desc:'Существует вне времени',           sell:1900},
  legend_amulet:   {n:'Амулет Вечности',      i:'📿', t:'amulet', r:'legendary',atk:15, def:20, hp:100, crit:9,  desc:'Дарует бессмертие духу',           sell:1900},
  phoenix_heart:   {n:'Сердце Феникса',       i:'🦅', t:'amulet', r:'legendary',atk:20, def:15, hp:120, crit:8,  desc:'Возрождение при смерти',           sell:2100},
  legend_boots:    {n:'Сапоги Легенды',       i:'👢', t:'boots',  r:'legendary',atk:12, def:25, hp:80,  crit:8,  desc:'Быстрее ветра',                    sell:1650},
  legend_pants:    {n:'Латы Паладина',        i:'👖', t:'pants',  r:'legendary',atk:10, def:28, hp:90,  crit:6,  desc:'Носил великий паладин',            sell:1700},
  legend_gloves:   {n:'Перчатки Титана',      i:'🧤', t:'gloves', r:'legendary',atk:18, def:15, hp:60,  crit:10, desc:'Сила великанов',                   sell:1750},
  // ── MYTHIC ──────────────────────────────────────────────────────
  mythic_reaper:   {n:'Жнец Бездны [МИФ]',   i:'👿', t:'weapon', r:'mythic',   atk:100,def:25, hp:-30, crit:20, desc:'Абсолютная тьма',                  sell:8000},
  mythic_armor:    {n:'Доспех Богов [МИФ]',   i:'⚡', t:'armor',  r:'mythic',   atk:20, def:60, hp:200, crit:8,  desc:'Непробиваемый',                    sell:9000},
  mythic_helm:     {n:'Корона Тьмы [МИФ]',    i:'👑', t:'helmet', r:'mythic',   atk:25, def:45, hp:150, crit:15, desc:'Правитель нечисти',                sell:7500},
  mythic_blade:    {n:'Клинок Апокалипсиса [МИФ]',i:'🌟',t:'weapon',r:'mythic', atk:120,def:20, hp:0,   crit:25, desc:'Разрывает реальность',             sell:12000},
  mythic_ring:     {n:'Кольцо Бога [МИФ]',    i:'💫', t:'ring',   r:'mythic',   atk:30, def:30, hp:200, crit:15, desc:'Божественная сила',                sell:10000},
  mythic_boots:    {n:'Сапоги Вечности [МИФ]',i:'✨', t:'boots',  r:'mythic',   atk:15, def:40, hp:150, crit:12, desc:'Шагают между мирами',              sell:8500},
};

// ── ITEM POOLS с процентами выпадения ──────────────────────────────
// w = вес. Шанс = w / сумма_всех_w * 100%
// Также глобальный шанс дропа 38% (см. tryDrop)
var ITEM_POOLS={
  // Лес — обычные (wolf, goblin)        суммарный вес = 100
  pf_common:   [{w:35,id:'worn_sword'},{w:25,id:'leather_gloves'},{w:18,id:'iron_ring'},
                {w:10,id:'wooden_club'},{w:6,id:'cloth_boots'},{w:4,id:'hunters_bow'},{w:2,id:'elven_blade'}],
  // Лес — необычные (bandit)            вес = 100
  pf_uncommon: [{w:30,id:'hunters_bow'},{w:22,id:'leather_armor'},{w:18,id:'silver_ring'},
                {w:12,id:'chain_pants'},{w:8,id:'forest_cloak'},{w:6,id:'elven_blade'},{w:4,id:'druid_amulet'}],

  // Пещера — обычные (skeleton,spider,bat)  вес = 100
  pc_common:   [{w:35,id:'bone_dagger'},{w:25,id:'iron_helmet'},{w:18,id:'cave_ring'},
                {w:10,id:'tattered_pants'},{w:7,id:'steel_sword'},{w:5,id:'shadow_hood'}],
  // Пещера — редкие (golem, darkmage)   вес = 100
  pc_rare:     [{w:28,id:'steel_sword'},{w:22,id:'chain_pants'},{w:18,id:'shadow_hood'},
                {w:14,id:'mana_ring'},{w:10,id:'cursed_blade'},{w:6,id:'frost_axe'},{w:2,id:'war_helmet'}],

  // Руины — обычные (zombie)            вес = 100
  pr_common:   [{w:30,id:'steel_sword'},{w:25,id:'plate_armor'},{w:20,id:'rune_helmet'},
                {w:12,id:'cursed_blade'},{w:8,id:'runic_armor'},{w:5,id:'arcane_staff'}],
  // Руины — редкие (golem,darkmage)     вес = 100
  pr_rare:     [{w:25,id:'arcane_staff'},{w:20,id:'plate_armor'},{w:18,id:'rune_helmet'},
                {w:14,id:'guardian_ring'},{w:10,id:'arcane_amulet'},{w:8,id:'thunder_wand'},
                {w:4,id:'soul_crown'},{w:1,id:'paladin_armor'}],

  // Вулкан — необычные (fire_elem,lava_troll)   вес = 100
  pv_uncommon: [{w:30,id:'dragon_scale'},{w:25,id:'flame_sword'},{w:18,id:'guardian_ring'},
                {w:12,id:'dragon_helm'},{w:8,id:'lava_armor'},{w:5,id:'phoenix_amulet'},{w:2,id:'storm_hammer'}],
  // Вулкан — редкие (dragonling)        вес = 100
  pv_rare:     [{w:28,id:'flame_sword'},{w:22,id:'dragon_helm'},{w:18,id:'volcano_boots'},
                {w:14,id:'phoenix_amulet'},{w:8,id:'inferno_pants'},{w:6,id:'void_blade'},
                {w:3,id:'inferno_blade'},{w:1,id:'thunder_blade'}],

  // Бездна — редкие (demon)             вес = 100
  pa_rare:     [{w:28,id:'soul_crown'},{w:22,id:'void_armor'},{w:18,id:'death_ring'},
                {w:14,id:'shadow_blade'},{w:10,id:'shadow_mask'},{w:6,id:'abyss_boots'},{w:2,id:'shadow_pants'}],
  // Бездна — эпические (lich,shadow_knight)  вес = 100
  pa_epic:     [{w:22,id:'shadow_blade'},{w:18,id:'void_armor'},{w:15,id:'lich_staff'},
                {w:13,id:'death_ring'},{w:10,id:'abyss_boots'},{w:8,id:'void_amulet'},
                {w:6,id:'war_gloves'},{w:4,id:'soul_reaver'},{w:3,id:'mythic_reaper'},{w:1,id:'mythic_ring'}],

  // Горы — обычные (ice_troll,snow_wolf,ice_guardian)  вес = 100
  pm_common:   [{w:30,id:'steel_sword'},{w:22,id:'plate_armor'},{w:18,id:'rune_helmet'},
                {w:14,id:'battle_gloves'},{w:10,id:'iron_boots'},{w:6,id:'dragon_scale'}],
  // Горы — редкие (stone_drake,frost_mage,harpy)  вес = 100
  pm_rare:     [{w:25,id:'dragon_scale'},{w:20,id:'flame_sword'},{w:18,id:'dragon_helm'},
                {w:14,id:'phoenix_amulet'},{w:10,id:'void_armor'},{w:7,id:'frost_axe'},
                {w:4,id:'dragon_lord_helm'},{w:2,id:'inferno_blade'}],
};

// CASES
var CASES=[
  {id:'forest_case',   name:'Лесной сундук',    icon:'📦', price:200,  color:'#27ae60', desc:'Снаряжение охотника и лесных духов',
   pools:['pf_common','pf_common','pf_uncommon'], rarities:['common','uncommon','rare']},
  {id:'dungeon_case',  name:'Подземный сундук',  icon:'⚰', price:500,  color:'#3498db', desc:'Артефакты пещер и руин',
   pools:['pc_common','pc_rare','pr_common','pr_rare'], rarities:['uncommon','rare','epic']},
  {id:'mountain_case', name:'Горный сундук',     icon:'⛰', price:800,  color:'#aaaacc', desc:'Снаряжение из ледяных гор',
   pools:['pm_common','pm_common','pm_rare'], rarities:['uncommon','rare','epic']},
  {id:'dragon_case',   name:'Драконий сундук',   icon:'🐲', price:1500, color:'#e67e22', desc:'Сокровища вулкана и драконов',
   pools:['pv_uncommon','pv_rare','pa_rare'], rarities:['rare','epic','legendary']},
  {id:'abyss_case',    name:'Сундук Бездны',     icon:'🌀', price:5000, color:'#9b59b6', desc:'Тёмные артефакты из глубин',
   pools:['pa_rare','pa_epic','pa_epic'], rarities:['epic','legendary','mythic']},
  {id:'mythic_case',   name:'Мифический сундук', icon:'💫', price:15000,color:'#e74c3c', desc:'Шанс на мифический предмет',
   pools:['pa_epic','pa_epic','pa_epic'], rarities:['legendary','mythic','mythic']},
];
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
  // Validate nick BEFORE disabling button
  var nick='';
  if(authIsReg){
    nick=document.getElementById('a-nick').value.trim();
    if(!nick||nick.length<2){err.textContent='Имя героя: мин. 2 символа';return;}
  }
  btn.disabled=true;btn.textContent='Загрузка...';
  try{
    var data;
    if(authIsReg){
      data=await api('/api/register',{login:login,password:pass,nick:nick});
    } else {
      data=await api('/api/login',{login:login,password:pass});
    }
    curUser={login:data.login,nick:data.nick,passhash:data.passhash};
    // Init all player fields before loadGD
    P.house={furniture:[]};
    P.quests={completed:[],progress:{}};
    P.enchants={};
    P.pet=null;
    P.clan=null;
    P.trades=[];
    if(data.game_data&&Object.keys(data.game_data).length)loadGD(data.game_data);
    recalcStats();startGame();
  }catch(e){err.textContent=e.message||'Ошибка сервера';}
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
  if(d.house)P.house=d.house;else P.house={furniture:[]};
  if(d.quests)P.quests=d.quests;else P.quests={completed:[],progress:{}};
  if(d.enchants)P.enchants=d.enchants;else P.enchants={};
  P.pet=d.pet||null;
  P.clan=d.clan||null;
  P.trades=d.trades||[];
}
function getGD(){
  return{hp:P.hp,maxHp:P.maxHp,gold:P.gold,level:P.level,xp:P.xp,kills:P.kills,totalKills:P.totalKills,
    crit:P.crit,dodge:P.dodge,talentPoints:P.talentPoints,zone:currentZone,
    inventory:P.inventory,equipped:P.equipped,talents:P.talents,invOrder:invAddOrder,
    house:P.house,quests:P.quests,enchants:P.enchants,pet:P.pet,clan:P.clan,trades:P.trades};
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
  // Enchantments
  if(P.enchants){for(var eid in P.enchants){var elv=P.enchants[eid]||0;bonusAtk+=elv*5;bonusDef+=elv*5;}}
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
  // Pet bonuses
  var pd=getPetDef();
  if(pd){bonusAtk+=pd.atkBonus||0;bonusDef+=pd.defBonus||0;bonusHp+=pd.hpBonus||0;bonusCrit+=pd.critBonus||0;}
  // House HP bonus
  if(P.house&&P.house.furniture){
    P.house.furniture.forEach(function(fid){
      var f=FURNITURE?FURNITURE.find(function(x){return x.id===fid;}):null;
      if(f&&f.buff==='hp'&&f.buffPct)bonusHp+=Math.floor(baseHp*f.buffVal/100);
      if(f&&f.buff==='def'&&f.buffPct)bonusDef+=Math.floor(baseDef*f.buffVal/100);
      if(f&&f.buff==='crit'&&!f.buffPct)bonusCrit+=f.buffVal;
    });
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
  amount=Math.floor(amount*getHouseXpMult()*getClanXpMult());
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
  mult*=getHouseGoldMult();
  mult*=getClanGoldMult();
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
  // Safety defaults (in case loadGD wasn't called or missed fields)
  if(!P.house)P.house={furniture:[]};
  if(!P.quests)P.quests={completed:[],progress:{}};
  if(!P.enchants)P.enchants={};
  if(P.pet===undefined)P.pet=null;
  if(!P.clan)P.clan=null;
  if(!P.trades)P.trades=[];
  recalcStats();
  updateHdr();updateMapUI();buildTalentTree();buildShop();buildRaids();updatePetHdr();
  checkIncomingTrades();
  goTab('world');
  if(!loopsOn){loopsOn=true;
    setInterval(function(){if(curUser)saveGame(false);},25000);
    setInterval(function(){
      if(curTab==='chat')loadChat();
      if(curTab==='friends')loadFriends();
      if(activeRaidId&&curTab==='raid')pollRaid();
      if(curTab==='clan')buildClan();
    },3500);
  }
}

// ═══════════════════════════════════════
// TABS
// ═══════════════════════════════════════
function goTab(name){
  curTab=name;
  var names=['world','battle','inv','talents','shop','raid','clan','chat','friends','lead'];
  document.querySelectorAll('.tab').forEach(function(t,i){t.className='tab'+(names[i]===name?' on':'');});
  document.querySelectorAll('.panel').forEach(function(p){p.style.display='none';});
  var el=document.getElementById('p-'+name);if(!el)return;
  if(name==='inv')el.style.display='grid';
  else el.style.display='flex';
  if(name==='world')updateMapUI();
  if(name==='inv'){updateEquipSlots();updateInvGrid();updateInvStats();}
  if(name==='talents')updateTalentTree();
  if(name==='shop'){document.getElementById('shop-gold').textContent=fmt(P.gold);}
  if(name==='chat')loadChat();
  if(name==='friends')loadFriends();
  if(name==='lead')loadLead();
  if(name==='raid')buildRaids();
  if(name==='clan')buildClan();
}

// ═══════════════════════════════════════
// PETS
// ═══════════════════════════════════════
var PETS_DEF=[
  {id:'wolf_pup',  name:'Волчонок',    icon:'🐺', price:500,  atkBonus:5,  defBonus:0,  hpBonus:0,  critBonus:2, dmgPct:8,  desc:'Кусает врагов. +8% доп. урон, +5 ATK, +2% крит'},
  {id:'cat',       name:'Чёрный кот',  icon:'🐈', price:400,  atkBonus:0,  defBonus:0,  hpBonus:0,  critBonus:5, dmgPct:5,  desc:'Приносит удачу. +5% доп. урон, +5% крит'},
  {id:'owl',       name:'Совёнок',     icon:'🦉', price:600,  atkBonus:0,  defBonus:5,  hpBonus:30, critBonus:0, dmgPct:4,  desc:'Защищает хозяина. +4% доп. урон, +5 DEF, +30 HP'},
  {id:'snake',     name:'Змейка',      icon:'🐍', price:700,  atkBonus:8,  defBonus:0,  hpBonus:0,  critBonus:3, dmgPct:10, desc:'Ядовитые укусы. +10% доп. урон, +8 ATK'},
  {id:'dragon_egg',name:'Дракончик',   icon:'🐲', price:2500, atkBonus:15, defBonus:8,  hpBonus:50, critBonus:5, dmgPct:18, desc:'Легендарный питомец! +18% доп. урон, +15 ATK, +8 DEF, +50 HP'},
  {id:'phoenix',   name:'Феникс',      icon:'🦅', price:5000, atkBonus:20, defBonus:10, hpBonus:80, critBonus:8, dmgPct:25, desc:'Мифический! +25% доп. урон, воскрешает при смерти (1/бой)'},
];

function openPetShop(){
  if(!P.pet)P.pet=null;
  var cur=document.getElementById('pet-current');
  var list=document.getElementById('pet-list');
  if(P.pet){
    var pd=PETS_DEF.find(function(x){return x.id===P.pet.id;});
    cur.innerHTML='<div style="background:rgba(39,174,96,.1);border:1px solid #27ae60;border-radius:10px;padding:12px;margin-bottom:10px;display:flex;align-items:center;gap:10px">'
      +'<div style="font-size:36px">'+P.pet.icon+'</div>'
      +'<div><div style="font-size:14px;font-weight:bold;color:#27ae60">'+esc(P.pet.name)+'</div>'
      +'<div style="font-size:11px;color:#666;margin-top:2px">'+(pd?esc(pd.desc):'')+'</div>'
      +'<div style="font-size:11px;color:#e74c3c;margin-top:4px;cursor:pointer" onclick="releasePet()">✕ Отпустить питомца</div>'
      +'</div></div>';
  } else {
    cur.innerHTML='<div style="font-size:12px;color:#555;margin-bottom:8px">У тебя нет питомца</div>';
  }
  list.innerHTML='';
  PETS_DEF.forEach(function(p){
    var owned=P.pet&&P.pet.id===p.id;
    var div=document.createElement('div');
    div.style.cssText='display:flex;align-items:center;gap:10px;padding:10px;margin-bottom:6px;border-radius:9px;border:1px solid '+(owned?'#27ae60':'var(--border)')+';background:'+(owned?'rgba(39,174,96,.07)':'#0d0d18');
    div.innerHTML='<div style="font-size:28px">'+p.icon+'</div>'
      +'<div style="flex:1"><div style="font-size:13px;font-weight:bold;color:#d4c9a8">'+esc(p.name)+'</div>'
      +'<div style="font-size:10px;color:#666;margin-top:2px">'+esc(p.desc)+'</div></div>'
      +(owned?'<div style="font-size:11px;color:#27ae60;font-weight:bold">✓ Активен</div>'
        :'<button onclick="buyPet(\''+p.id+'\')" style="padding:6px 10px;border-radius:7px;border:none;background:var(--purple);color:#fff;font-size:11px;cursor:pointer">💰 '+p.price+'g</button>');
    list.appendChild(div);
  });
  document.getElementById('pet-modal-bg').style.display='flex';
}
function closePetShop(){document.getElementById('pet-modal-bg').style.display='none';}
function buyPet(pid){
  var p=PETS_DEF.find(function(x){return x.id===pid;});if(!p)return;
  if(P.gold<p.price){toast('Нужно '+p.price+' золота','#e74c3c');return;}
  if(P.pet&&P.pet.id===pid){toast('Этот питомец уже у тебя!','#555');return;}
  P.gold-=p.price;
  P.pet={id:p.id,name:p.name,icon:p.icon};
  recalcStats();updateHdr();updatePetHdr();
  toast(p.icon+' '+p.name+' теперь твой питомец!','#27ae60');
  openPetShop();
}
function releasePet(){
  if(!P.pet)return;
  if(!confirm('Отпустить питомца '+P.pet.name+'?'))return;
  P.pet=null;
  recalcStats();updateHdr();updatePetHdr();
  toast('Питомец отпущен','#555');
  openPetShop();
}
function getPetDef(){
  if(!P.pet)return null;
  return PETS_DEF.find(function(x){return x.id===P.pet.id;})||null;
}
function updatePetHdr(){
  var wrap=document.getElementById('h-pet-wrap');
  var name=document.getElementById('h-pet-name');
  if(!wrap||!name)return;
  if(P.pet){wrap.style.display='';name.textContent=P.pet.icon+' '+P.pet.name;}
  else{wrap.style.display='none';}
}
// Pet attack in battle — called after player hits
function petAttack(enemyDef){
  var pd=getPetDef();if(!pd)return 0;
  var base=Math.max(1,Math.floor(P.atk*pd.dmgPct/100)-Math.floor((enemyDef||0)*0.3));
  return Math.floor(base*(0.7+Math.random()*0.6));
}

// ═══════════════════════════════════════
// CLAN SYSTEM
// ═══════════════════════════════════════
var clanData=null;
var CLAN_LEVELS=[
  {lv:1,name:'Новичок',   maxMembers:5,  bonus:''},
  {lv:2,name:'Отряд',     maxMembers:10, bonus:'+5% XP'},
  {lv:3,name:'Дружина',   maxMembers:15, bonus:'+10% XP, +5% Gold'},
  {lv:4,name:'Орден',     maxMembers:20, bonus:'+15% XP, +10% Gold'},
  {lv:5,name:'Легион',    maxMembers:30, bonus:'+20% XP, +15% Gold, +5% ATK'},
];

function buildClan(){
  var content=document.getElementById('clan-content');if(!content)return;
  if(!P.clan){
    content.innerHTML='<div style="background:var(--card);border-radius:12px;border:1px solid var(--border);padding:20px;text-align:center">'
      +'<div style="font-size:48px;margin-bottom:10px">⚜</div>'
      +'<div style="font-size:16px;font-weight:bold;color:var(--gold);margin-bottom:8px">У тебя нет клана</div>'
      +'<div style="font-size:12px;color:#555;margin-bottom:16px">Создай свой клан или вступи в существующий</div>'
      +'<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap">'
      +'<div style="flex:1;min-width:200px;background:#0d0d18;border:1px solid var(--border);border-radius:10px;padding:14px">'
      +'<div style="font-size:14px;font-weight:bold;color:#d4c9a8;margin-bottom:8px">Создать клан</div>'
      +'<input id="clan-name-inp" placeholder="Название клана (2-16 симв.)" style="width:100%;padding:8px;border-radius:7px;border:1px solid var(--border);background:#080810;color:#d4c9a8;font-size:13px;outline:none;margin-bottom:6px">'
      +'<input id="clan-tag-inp" placeholder="Тег [3-4 симв.]" style="width:100%;padding:8px;border-radius:7px;border:1px solid var(--border);background:#080810;color:#d4c9a8;font-size:13px;outline:none;margin-bottom:8px">'
      +'<button onclick="createClan()" style="width:100%;padding:9px;border-radius:8px;border:none;background:var(--purple);color:#fff;font-size:13px;font-weight:bold;cursor:pointer">⚜ Создать (500g)</button>'
      +'</div>'
      +'<div style="flex:1;min-width:200px;background:#0d0d18;border:1px solid var(--border);border-radius:10px;padding:14px">'
      +'<div style="font-size:14px;font-weight:bold;color:#d4c9a8;margin-bottom:8px">Вступить в клан</div>'
      +'<input id="clan-join-inp" placeholder="Название или тег клана" style="width:100%;padding:8px;border-radius:7px;border:1px solid var(--border);background:#080810;color:#d4c9a8;font-size:13px;outline:none;margin-bottom:8px">'
      +'<button onclick="joinClan()" style="width:100%;padding:9px;border-radius:8px;border:none;background:#1a5c28;color:#fff;font-size:13px;font-weight:bold;cursor:pointer">➜ Вступить</button>'
      +'</div>'
      +'</div>'
      +'<div style="margin-top:16px;border-top:1px solid var(--border);padding-top:14px">'
      +'<div style="font-size:12px;font-weight:bold;color:#555;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px">Бонусы кланов по уровням</div>'
      +CLAN_LEVELS.map(function(l){return '<div style="font-size:11px;color:#666;padding:3px 0">Lv'+l.lv+' «'+l.name+'» (до '+l.maxMembers+' чел.)'+( l.bonus?' — '+l.bonus:'')+'</div>';}).join('')
      +'</div>'
      +'</div>';
  } else {
    var c=P.clan;
    var lvInfo=CLAN_LEVELS[Math.min((c.level||1)-1,CLAN_LEVELS.length-1)];
    var isLeader=c.leader===curUser.nick;
    var members=c.members||[];
    content.innerHTML='<div style="background:var(--card);border-radius:12px;border:1px solid var(--border);padding:16px">'
      // Header
      +'<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">'
      +'<div style="font-size:36px">⚜</div>'
      +'<div style="flex:1">'
      +'<div style="font-size:18px;font-weight:bold;color:var(--gold)">['+esc(c.tag)+'] '+esc(c.name)+'</div>'
      +'<div style="font-size:11px;color:#666;margin-top:2px">Lv'+c.level+' «'+lvInfo.name+'» · '+members.length+'/'+lvInfo.maxMembers+' участников</div>'
      +(lvInfo.bonus?'<div style="font-size:11px;color:#27ae60;margin-top:2px">'+lvInfo.bonus+'</div>':'')
      +'</div>'
      +(isLeader?'<button onclick="upgradeClan()" style="padding:6px 12px;border-radius:7px;border:none;background:var(--gold);color:#000;font-size:11px;font-weight:bold;cursor:pointer">▲ Прокачать</button>':'')
      +'</div>'
      // XP bar
      +'<div style="margin-bottom:14px">'
      +'<div style="display:flex;justify-content:space-between;font-size:10px;color:#555;margin-bottom:3px"><span>Опыт клана</span><span>'+(c.xp||0)+' / '+(c.level||1)*1000+'</span></div>'
      +'<div style="height:6px;background:#1a1a2e;border-radius:3px"><div style="width:'+Math.min(100,Math.round(((c.xp||0)/((c.level||1)*1000))*100))+'%;height:6px;background:var(--gold);border-radius:3px"></div></div>'
      +'</div>'
      // Members
      +'<div style="font-size:11px;color:#555;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px">Участники</div>'
      +'<div style="display:flex;flex-direction:column;gap:5px;margin-bottom:14px">'
      +members.map(function(m){
        return '<div style="display:flex;align-items:center;gap:8px;padding:8px 10px;background:#0d0d18;border-radius:8px;border:1px solid var(--border)">'
          +'<div style="font-size:16px">'+(m.nick===c.leader?'👑':'⚔')+'</div>'
          +'<div style="flex:1"><div style="font-size:12px;font-weight:bold;color:#d4c9a8">'+esc(m.nick)+'</div>'
          +'<div style="font-size:10px;color:#555">Lv'+m.level+'</div></div>'
          +(isLeader&&m.nick!==curUser.nick?'<button onclick="kickMember(\''+esc(m.nick)+'\')" style="padding:3px 8px;border-radius:5px;border:none;background:#3d1a1a;color:#e74c3c;font-size:10px;cursor:pointer">Кик</button>':'')
          +'</div>';
      }).join('')
      +'</div>'
      // Actions
      +'<div style="display:flex;gap:8px;flex-wrap:wrap">'
      +(isLeader
        ?'<button onclick="disbandClan()" style="padding:8px 14px;border-radius:8px;border:none;background:#3d1a1a;color:#e74c3c;font-size:12px;cursor:pointer">💀 Распустить</button>'
        :'<button onclick="leaveClan()" style="padding:8px 14px;border-radius:8px;border:none;background:#3d1a1a;color:#e74c3c;font-size:12px;cursor:pointer">🚪 Покинуть</button>')
      +(isLeader?'<button onclick="inviteToClan()" style="padding:8px 14px;border-radius:8px;border:none;background:#1a3d1a;color:#27ae60;font-size:12px;cursor:pointer">➕ Пригласить</button>':'')
      +'<button onclick="donateToClan()" style="padding:8px 14px;border-radius:8px;border:none;background:rgba(201,162,39,.1);color:var(--gold);font-size:12px;cursor:pointer;border:1px solid #5a4a10">💰 Взнос (+50 xp)</button>'
      +'</div>'
      +'</div>';
  }
}

function createClan(){
  var name=(document.getElementById('clan-name-inp').value||'').trim();
  var tag=(document.getElementById('clan-tag-inp').value||'').trim().toUpperCase();
  if(name.length<2||name.length>16){toast('Название: 2-16 символов','#e74c3c');return;}
  if(tag.length<2||tag.length>4){toast('Тег: 2-4 символа','#e74c3c');return;}
  if(P.gold<500){toast('Нужно 500 золота','#e74c3c');return;}
  P.gold-=500;
  P.clan={name:name,tag:tag,level:1,xp:0,leader:curUser.nick,
    members:[{nick:curUser.nick,level:P.level}]};
  recalcStats();updateHdr();buildClan();
  toast('Клан ['+tag+'] '+name+' создан!','#c9a227');
}
function joinClan(){
  var inp=(document.getElementById('clan-join-inp').value||'').trim();
  if(!inp){toast('Введи название клана','#e74c3c');return;}
  // Offline-only: in a real game this would be server-side
  toast('Функция вступления требует сервера. Попроси лидера добавить тебя.','#555');
}
function leaveClan(){
  if(!P.clan)return;
  if(!confirm('Покинуть клан?'))return;
  P.clan=null;buildClan();toast('Ты покинул клан','#555');
}
function disbandClan(){
  if(!P.clan)return;
  if(!confirm('Распустить клан? Это нельзя отменить.'))return;
  P.clan=null;buildClan();toast('Клан распущен','#555');
}
function upgradeClan(){
  if(!P.clan)return;
  var curLv=P.clan.level||1;
  if(curLv>=CLAN_LEVELS.length){toast('Максимальный уровень клана!','#555');return;}
  var cost=(curLv)*2000;
  if(P.gold<cost){toast('Нужно '+cost+' золота для прокачки','#e74c3c');return;}
  P.gold-=cost;P.clan.level=curLv+1;P.clan.xp=0;
  updateHdr();buildClan();
  toast('Клан прокачан до Lv'+(curLv+1)+'!','#c9a227');
}
function donateToClan(){
  if(!P.clan)return;
  if(P.gold<100){toast('Нужно 100 золота для взноса','#e74c3c');return;}
  P.gold-=100;P.clan.xp=(P.clan.xp||0)+50;
  updateHdr();buildClan();toast('+50 xp клана!','#c9a227');
}
function inviteToClan(){
  var nick=prompt('Введи ник игрока для приглашения:');
  if(!nick)return;
  nick=nick.trim();
  if(!nick){return;}
  toast('Приглашение отправлено '+nick+' (в реальной игре — через сервер)','#27ae60');
}
function kickMember(nick){
  if(!P.clan)return;
  if(!confirm('Выгнать '+nick+' из клана?'))return;
  P.clan.members=P.clan.members.filter(function(m){return m.nick!==nick;});
  buildClan();toast(nick+' исключён из клана','#e74c3c');
}
function getClanXpMult(){
  if(!P.clan)return 1;
  var lv=P.clan.level||1;
  return 1+(lv>=2?0.05:0)+(lv>=3?0.05:0)+(lv>=4?0.05:0)+(lv>=5?0.05:0);
}
function getClanGoldMult(){
  if(!P.clan)return 1;
  var lv=P.clan.level||1;
  return 1+(lv>=3?0.05:0)+(lv>=4?0.05:0)+(lv>=5?0.05:0);
}

// ═══════════════════════════════════════
// TRADE SYSTEM
// ═══════════════════════════════════════
var tradeSelectedUid=null;

function openTrade(){
  tradeSelectedUid=null;
  renderTradeItems();
  renderTradeIncoming();
  document.getElementById('trade-modal-bg').style.display='flex';
}
function closeTrade(){document.getElementById('trade-modal-bg').style.display='none';}

function renderTradeItems(){
  var grid=document.getElementById('trade-my-items');if(!grid)return;
  grid.innerHTML='';
  P.inventory.forEach(function(entry){
    var item=ITEMS[entry.id];if(!item)return;
    var sel=tradeSelectedUid===entry.uid;
    var cell=document.createElement('div');
    cell.style.cssText='background:'+(sel?'rgba(52,152,219,.2)':'#0d0d18')+';border:2px solid '+(sel?'#3498db':'#2a2540')+';border-radius:8px;padding:5px;display:flex;flex-direction:column;align-items:center;gap:2px;cursor:pointer;aspect-ratio:1';
    cell.innerHTML='<div style="font-size:20px">'+item.i+'</div><div style="font-size:8px;color:#888;text-align:center;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical">'+esc(item.n)+'</div>';
    (function(uid,nm,ic){cell.onclick=function(){
      tradeSelectedUid=uid;
      document.getElementById('trade-selected-item').style.display='';
      document.getElementById('trade-selected-name').textContent=ic+' '+nm;
      renderTradeItems();
    };})(entry.uid,item.n,item.i);
    grid.appendChild(cell);
  });
}

function renderTradeIncoming(){
  var wrap=document.getElementById('trade-incoming');if(!wrap)return;
  if(!P.trades||!P.trades.length){
    wrap.innerHTML='<div style="font-size:12px;color:#555">Нет входящих предложений</div>';
    return;
  }
  wrap.innerHTML=P.trades.map(function(t,i){
    var item=ITEMS[t.itemId]||{i:'?',n:'?'};
    return '<div style="display:flex;align-items:center;gap:8px;padding:8px;background:#0d0d18;border-radius:8px;margin-bottom:5px;border:1px solid var(--border)">'
      +'<div style="font-size:22px">'+item.i+'</div>'
      +'<div style="flex:1"><div style="font-size:12px;font-weight:bold;color:#d4c9a8">'+esc(item.n)+'</div>'
      +'<div style="font-size:10px;color:#555">от '+esc(t.from)+'</div></div>'
      +'<button onclick="acceptTrade('+i+')" style="padding:4px 8px;border-radius:5px;border:none;background:#27ae60;color:#fff;font-size:10px;cursor:pointer">✓</button>'
      +'<button onclick="declineTrade('+i+')" style="padding:4px 8px;border-radius:5px;border:none;background:#e74c3c;color:#fff;font-size:10px;cursor:pointer;margin-left:3px">✕</button>'
      +'</div>';
  }).join('');
}

function sendTradeOffer(){
  if(!tradeSelectedUid){toast('Выбери предмет','#e74c3c');return;}
  var target=(document.getElementById('trade-target-login').value||'').trim().toLowerCase();
  if(!target){toast('Введи логин получателя','#e74c3c');return;}
  if(target===curUser.login){toast('Нельзя отправить себе','#e74c3c');return;}
  var entry=P.inventory.find(function(x){return x.uid===tradeSelectedUid;});
  if(!entry){toast('Предмет не найден','#e74c3c');return;}
  var item=ITEMS[entry.id];if(!item)return;
  // Remove from inventory
  var isEq=isEquipped(entry.id);
  var others=P.inventory.filter(function(x){return x.id===entry.id&&x.uid!==entry.uid;});
  if(isEq&&others.length===0){for(var s in P.equipped)if(P.equipped[s]===entry.id)P.equipped[s]=null;}
  P.inventory=P.inventory.filter(function(x){return x.uid!==entry.uid;});
  // Store trade in target's pending (simulated via localStorage key since we have no server endpoint)
  // In production this would be an API call
  var tradeObj={from:curUser.nick,fromLogin:curUser.login,itemId:entry.id,uid:entry.uid,ts:Date.now()};
  // Store in local pending for demo — we piggyback on the save system
  var pending=JSON.parse(localStorage.getItem('pending_trades_'+target)||'[]');
  pending.push(tradeObj);
  localStorage.setItem('pending_trades_'+target,JSON.stringify(pending));
  tradeSelectedUid=null;
  recalcStats();updateHdr();updateInvGrid();
  toast('📤 Отправлено '+item.n+' → '+target,'#3498db');
  closeTrade();
}

function checkIncomingTrades(){
  if(!curUser)return;
  var pending=JSON.parse(localStorage.getItem('pending_trades_'+curUser.login)||'[]');
  if(pending.length){
    P.trades=(P.trades||[]).concat(pending);
    localStorage.removeItem('pending_trades_'+curUser.login);
  }
}

function acceptTrade(idx){
  if(!P.trades||!P.trades[idx])return;
  var t=P.trades[idx];
  var item=ITEMS[t.itemId];if(!item){P.trades.splice(idx,1);renderTradeIncoming();return;}
  var uid=t.uid||Date.now()+'_tr';
  P.inventory.push({id:t.itemId,uid:uid,ts:Date.now()});
  invAddOrder.push(uid);
  P.trades.splice(idx,1);
  updateInvGrid();renderTradeIncoming();
  toast('✓ Принято: '+item.i+' '+item.n,'#27ae60');
}

function declineTrade(idx){
  if(!P.trades||!P.trades[idx])return;
  P.trades.splice(idx,1);
  renderTradeIncoming();
  toast('Предложение отклонено','#555');
}

// HOUSE FURNITURE
var FURNITURE=[
  {id:'bed',     name:'Кровать',      icon:'🛏', price:200,  buff:'atk',   buffVal:2,  buffPct:true,  desc:'+2% к урону в бою'},
  {id:'fireplace',name:'Камин',       icon:'🔥', price:350,  buff:'def',   buffVal:3,  buffPct:true,  desc:'+3% к защите'},
  {id:'bookshelf',name:'Книжная полка',icon:'📚',price:500,  buff:'xp',    buffVal:10, buffPct:true,  desc:'+10% к получаемому XP'},
  {id:'trophy',  name:'Охотничий трофей',icon:'🦌',price:400,buff:'crit',  buffVal:2,  buffPct:false, desc:'+2% к крит. шансу'},
  {id:'chest',   name:'Сундук',       icon:'📦', price:600,  buff:'gold',  buffVal:5,  buffPct:true,  desc:'+5% к золоту с врагов'},
  {id:'altar',   name:'Алтарь',       icon:'🕯', price:800,  buff:'hp',    buffVal:5,  buffPct:true,  desc:'+5% к макс. HP'},
];
if(!P.house)P.house={furniture:[]};

// QUESTS
var QUESTS_DEF=[
  {id:'q_kills10',   name:'Охотник',      icon:'⚔', desc:'Убей 10 врагов',          type:'kills',  target:10,  reward:{gold:150,xp:100}},
  {id:'q_kills50',   name:'Истребитель',  icon:'💀', desc:'Убей 50 врагов',          type:'kills',  target:50,  reward:{gold:500,xp:400}},
  {id:'q_kills100',  name:'Мясник',       icon:'🗡', desc:'Убей 100 врагов',         type:'kills',  target:100, reward:{gold:1200,xp:1000}},
  {id:'q_gold500',   name:'Накопитель',   icon:'💰', desc:'Собери 500 золота',        type:'gold',   target:500, reward:{gold:200,xp:150}},
  {id:'q_gold2000',  name:'Торговец',     icon:'🪙', desc:'Собери 2000 золота',       type:'gold',   target:2000,reward:{gold:800,xp:500}},
  {id:'q_level5',    name:'Ученик',       icon:'⭐', desc:'Достигни 5 уровня',        type:'level',  target:5,   reward:{gold:300,xp:0}},
  {id:'q_level10',   name:'Воин',         icon:'🌟', desc:'Достигни 10 уровня',       type:'level',  target:10,  reward:{gold:1000,xp:0}},
  {id:'q_level20',   name:'Легенда',      icon:'💫', desc:'Достигни 20 уровня',       type:'level',  target:20,  reward:{gold:5000,xp:0}},
  {id:'q_cave',      name:'Исследователь',icon:'🕳', desc:'Зайди в Пещеру Ужаса',    type:'zone',   target:'cave',  reward:{gold:200,xp:120}},
  {id:'q_volcano',   name:'Огнеборец',    icon:'🌋', desc:'Зайди в Огненную Гору',   type:'zone',   target:'volcano',reward:{gold:600,xp:400}},
];
if(!P.quests)P.quests={completed:[],progress:{}};

// MAP LOCATION
var currentMapLoc='village';

function switchMapLoc(loc){
  if(loc==='mountains'&&P.level<10){toast('Нужен уровень 10 для гор!','#e74c3c');return;}
  currentMapLoc=loc;
  document.getElementById('map-village').style.display=loc==='village'?'block':'none';
  document.getElementById('map-mountains').style.display=loc==='mountains'?'block':'none';
  document.getElementById('maploc-village').className='sort-btn'+(loc==='village'?' on':'');
  document.getElementById('maploc-mountains').className='sort-btn'+(loc==='mountains'?' on':'');
  updateMapUI();
}

// ═══════════════════════════════════════
// MY HOUSE
// ═══════════════════════════════════════
function openMyHouse(){
  if(!P.house)P.house={furniture:[]};
  var list=document.getElementById('house-furniture-list');
  var buffsEl=document.getElementById('house-buffs-list');
  list.innerHTML='';
  FURNITURE.forEach(function(f){
    var owned=P.house.furniture.indexOf(f.id)!==-1;
    var div=document.createElement('div');
    div.style.cssText='display:flex;align-items:center;gap:10px;padding:10px;margin-bottom:6px;border-radius:9px;border:1px solid '+(owned?'#27ae60':'var(--border)')+';background:'+(owned?'rgba(39,174,96,.08)':'#0d0d18');
    div.innerHTML='<div style="font-size:24px">'+f.icon+'</div>'
      +'<div style="flex:1"><div style="font-size:13px;font-weight:bold;color:#d4c9a8">'+esc(f.name)+'</div>'
      +'<div style="font-size:11px;color:#666;margin-top:2px">'+esc(f.desc)+'</div></div>'
      +(owned
        ?'<div style="font-size:11px;color:#27ae60;font-weight:bold">✓ Есть</div>'
        :'<button onclick="buyFurniture(\''+f.id+'\')" style="padding:6px 12px;border-radius:7px;border:none;background:var(--purple);color:#fff;font-size:12px;cursor:pointer">💰 '+f.price+'g</button>');
    list.appendChild(div);
  });
  // Show active buffs
  var buffs=getHouseBuffs();
  buffsEl.innerHTML=buffs.length?buffs.map(function(b){return '✦ '+b;}).join('<br>'):'<span style="color:#555">Нет мебели — нет бафов</span>';
  document.getElementById('myhouse-modal-bg').style.display='flex';
}
function closeMyHouse(){document.getElementById('myhouse-modal-bg').style.display='none';}
function buyFurniture(fid){
  var f=FURNITURE.find(function(x){return x.id===fid;});
  if(!f)return;
  if(P.gold<f.price){toast('Мало золота! Нужно '+f.price,'#e74c3c');return;}
  if(P.house.furniture.indexOf(fid)!==-1){toast('Уже есть!','#555');return;}
  P.gold-=f.price;
  P.house.furniture.push(fid);
  updateHdr();recalcStats();
  toast('Куплено: '+f.name+' 🏠','#27ae60');
  openMyHouse();
}
function getHouseBuffs(){
  if(!P.house||!P.house.furniture)return[];
  var buffs=[];
  P.house.furniture.forEach(function(fid){
    var f=FURNITURE.find(function(x){return x.id===fid;});
    if(f)buffs.push(f.name+': '+f.desc);
  });
  return buffs;
}
function getHouseAtkMult(){
  if(!P.house||!P.house.furniture)return 1;
  var mult=1;
  P.house.furniture.forEach(function(fid){
    var f=FURNITURE.find(function(x){return x.id===fid;});
    if(f&&f.buff==='atk'&&f.buffPct)mult+=f.buffVal/100;
  });
  return mult;
}
function getHouseXpMult(){
  if(!P.house||!P.house.furniture)return 1;
  var mult=1;
  P.house.furniture.forEach(function(fid){
    var f=FURNITURE.find(function(x){return x.id===fid;});
    if(f&&f.buff==='xp'&&f.buffPct)mult+=f.buffVal/100;
  });
  return mult;
}
function getHouseGoldMult(){
  if(!P.house||!P.house.furniture)return 1;
  var mult=1;
  P.house.furniture.forEach(function(fid){
    var f=FURNITURE.find(function(x){return x.id===fid;});
    if(f&&f.buff==='gold'&&f.buffPct)mult+=f.buffVal/100;
  });
  return mult;
}

// ═══════════════════════════════════════
// FORGE
// ═══════════════════════════════════════
var ENCHANT_COST=150;
var ENCHANT_MAX=3;
function openForge(){
  var list=document.getElementById('forge-items-list');
  list.innerHTML='';
  if(!P.equipped||!Object.values(P.equipped).some(function(v){return v;})){
    list.innerHTML='<div style="color:#555;font-size:13px">Нет надетого снаряжения</div>';
  } else {
    Object.keys(P.equipped).forEach(function(slot){
      var id=P.equipped[slot];if(!id||!ITEMS[id])return;
      var item=ITEMS[id];
      var ench=P.enchants&&P.enchants[id]||0;
      var div=document.createElement('div');
      div.style.cssText='display:flex;align-items:center;gap:10px;padding:10px;margin-bottom:6px;border-radius:9px;border:1px solid var(--border);background:#0d0d18';
      div.innerHTML='<div style="font-size:22px">'+item.i+'</div>'
        +'<div style="flex:1"><div style="font-size:12px;font-weight:bold;color:#d4c9a8">'+esc(item.n)+'</div>'
        +'<div style="font-size:10px;color:#666">Зачарований: '+ench+'/'+ENCHANT_MAX+'</div>'
        +(ench>0?'<div style="font-size:10px;color:#e67e22">+'+ench*5+' ATK/DEF бонус</div>':'')
        +'</div>'
        +(ench<ENCHANT_MAX
          ?'<button onclick="enchantItem(\''+id+'\')" style="padding:6px 10px;border-radius:7px;border:none;background:#5c2a0a;color:#e67e22;font-size:11px;cursor:pointer;border:1px solid #7a4010">⚒ '+ENCHANT_COST+'g</button>'
          :'<div style="font-size:10px;color:#e67e22;font-weight:bold">МАКС</div>');
      list.appendChild(div);
    });
  }
  document.getElementById('forge-modal-bg').style.display='flex';
}
function closeForge(){document.getElementById('forge-modal-bg').style.display='none';}
function enchantItem(itemId){
  if(P.gold<ENCHANT_COST){toast('Нужно '+ENCHANT_COST+' золота','#e74c3c');return;}
  if(!P.enchants)P.enchants={};
  var cur=P.enchants[itemId]||0;
  if(cur>=ENCHANT_MAX){toast('Максимум зачарований!','#555');return;}
  P.gold-=ENCHANT_COST;
  P.enchants[itemId]=cur+1;
  recalcStats();updateHdr();
  toast('⚒ Зачарование '+ITEMS[itemId].n+' ('+(cur+1)+'/'+ENCHANT_MAX+')','#e67e22');
  openForge();
}

// ═══════════════════════════════════════
// QUEST BOARD
// ═══════════════════════════════════════
function openQuestBoard(){
  if(!P.quests)P.quests={completed:[],progress:{}};
  var list=document.getElementById('quest-list');
  list.innerHTML='';
  QUESTS_DEF.forEach(function(q){
    var done=P.quests.completed.indexOf(q.id)!==-1;
    var prog=getQuestProgress(q);
    var canClaim=!done&&prog>=q.target;
    var div=document.createElement('div');
    div.style.cssText='padding:10px 12px;margin-bottom:6px;border-radius:9px;border:1px solid '+(done?'#333':(canClaim?'#27ae60':'var(--border)'))+';background:'+(done?'#0a0a0a':(canClaim?'rgba(39,174,96,.07)':'#0d0d18'));
    var pct=Math.min(100,Math.round(prog/q.target*100));
    div.innerHTML='<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
      +'<div style="font-size:20px">'+q.icon+'</div>'
      +'<div style="flex:1"><div style="font-size:13px;font-weight:bold;color:'+(done?'#555':'#d4c9a8')+'">'+esc(q.name)+'</div>'
      +'<div style="font-size:11px;color:#555">'+esc(q.desc)+'</div></div>'
      +'<div style="font-size:11px;color:var(--gold)">💰'+q.reward.gold+(q.reward.xp?' +'+q.reward.xp+'xp':'')+'</div>'
      +'</div>'
      +(done?'<div style="font-size:11px;color:#555">✓ Выполнено</div>'
        :'<div style="height:6px;background:#1a1a2e;border-radius:3px;margin-bottom:6px"><div style="width:'+pct+'%;height:6px;background:'+(canClaim?'#27ae60':'#5c3d8f')+';border-radius:3px;transition:width .4s"></div></div>'
        +'<div style="display:flex;justify-content:space-between;align-items:center">'
        +'<span style="font-size:10px;color:#555">'+prog+'/'+q.target+'</span>'
        +(canClaim?'<button onclick="claimQuest(\''+q.id+'\')" style="padding:5px 12px;border-radius:6px;border:none;background:#27ae60;color:#fff;font-size:11px;cursor:pointer;font-weight:bold">Получить!</button>':'')
        +'</div>');
    list.appendChild(div);
  });
  document.getElementById('quest-modal-bg').style.display='flex';
}
function closeQuestBoard(){document.getElementById('quest-modal-bg').style.display='none';}
function getQuestProgress(q){
  if(q.type==='kills')return P.totalKills||0;
  if(q.type==='gold')return P.gold||0;
  if(q.type==='level')return P.level||1;
  if(q.type==='zone')return(P.quests.progress[q.id]||0);
  return 0;
}
function claimQuest(qid){
  var q=QUESTS_DEF.find(function(x){return x.id===qid;});
  if(!q||P.quests.completed.indexOf(qid)!==-1)return;
  if(getQuestProgress(q)<q.target){toast('Задание не выполнено!','#e74c3c');return;}
  P.quests.completed.push(qid);
  P.gold+=q.reward.gold;
  if(q.reward.xp)gainXP(q.reward.xp);
  updateHdr();
  toast('Задание выполнено! +'+q.reward.gold+' золота'+(q.reward.xp?' +'+q.reward.xp+' XP':''),'#c9a227');
  openQuestBoard();
}
function checkQuestZone(zoneId){
  if(!P.quests)P.quests={completed:[],progress:{}};
  QUESTS_DEF.forEach(function(q){
    if(q.type==='zone'&&q.target===zoneId&&P.quests.completed.indexOf(q.id)===-1){
      P.quests.progress[q.id]=1;
    }
  });
}

// ═══════════════════════════════════════
// MAP SHOP (redirects to shop tab)
// ═══════════════════════════════════════
function openMapShop(){goTab('shop');}

// ═══════════════════════════════════════
// DUNGEON ENGINE
// ═══════════════════════════════════════
var DNG={active:false,floor:1,room:0,maxRooms:5,hp:100,maxHp:100,log:[],zone:null,rooms:[]};
var DUNGEON_ZONES={
  forest:         {name:'Лесное подземелье',    icon:'🌲',floors:3,enemies:['wolf','goblin','bandit'],          bossPool:'forest_boss_dng',bg:'#0a1a0a'},
  cave:           {name:'Пещера Ужаса',          icon:'🕳',floors:5,enemies:['skeleton','spider','bat'],         bossPool:'cave_boss_dng',  bg:'#0a0a14'},
  ruins:          {name:'Руины',                 icon:'🏛',floors:5,enemies:['zombie','golem','darkmage'],       bossPool:'ruins_boss_dng', bg:'#1a1008'},
  volcano:        {name:'Вулканическое дно',     icon:'🌋',floors:7,enemies:['fire_elem','dragonling','lava_troll'],bossPool:'volcano_boss_dng',bg:'#1a0500'},
  abyss:          {name:'Глубины Бездны',        icon:'🌀',floors:8,enemies:['demon','lich','shadow_knight'],   bossPool:'abyss_boss_dng', bg:'#080010'},
  mountains:      {name:'Горное подземелье',     icon:'🏔',floors:5,enemies:['ice_troll','snow_wolf','harpy'],  bossPool:'mtn_boss_dng',   bg:'#0a0a1a'},
  mountains_boss: {name:'Логово Босса',          icon:'💀',floors:3,enemies:['stone_drake','ice_guardian','frost_mage'],bossPool:'mtn_boss_dng',bg:'#1a0505'},
};
var DNG_BOSSES={
  forest_boss_dng:  {name:'Лесной Король',     icon:'🌿',hp:500, maxHp:500, atk:25,def:8, gold:[80,150],  xp:300,  pool:'pf_uncommon'},
  cave_boss_dng:    {name:'Пещерный Дракон',   icon:'🐲',hp:800, maxHp:800, atk:35,def:12,gold:[150,250], xp:500,  pool:'pc_rare'},
  ruins_boss_dng:   {name:'Лич Руин',          icon:'☠', hp:700, maxHp:700, atk:40,def:10,gold:[130,220], xp:450,  pool:'pr_rare'},
  volcano_boss_dng: {name:'Огненный Титан',    icon:'🔥',hp:1200,maxHp:1200,atk:55,def:18,gold:[250,400], xp:700,  pool:'pv_rare'},
  abyss_boss_dng:   {name:'Повелитель Бездны', icon:'👿',hp:2000,maxHp:2000,atk:70,def:22,gold:[400,700], xp:1200, pool:'pa_epic'},
  mtn_boss_dng:     {name:'Горный Дракон',     icon:'🐲',hp:1000,maxHp:1000,atk:50,def:20,gold:[200,350], xp:600,  pool:'pm_rare'},
};
var DNG_ROOM_POOL=['combat','combat','combat','treasure','trap','rest','shop_room'];

function openDungeon(){
  var dz=DUNGEON_ZONES[currentZone];
  if(!dz){toast('В этой зоне нет подземелья','#555');return;}
  if(P.hp<=0){toast('Нужно HP для входа!','#e74c3c');return;}
  DNG.zone=currentZone; DNG.floor=1; DNG.log=[];
  DNG.hp=Math.ceil(P.hp); DNG.maxHp=P.maxHp; DNG.active=true;
  generateDungeonFloor();
  document.getElementById('dungeon-modal-bg').style.display='flex';
  renderDungeon();
}
function closeDungeon(){
  if(DNG.active){P.hp=Math.max(1,DNG.hp);updateHdr();}
  DNG.active=false;
  document.getElementById('dungeon-modal-bg').style.display='none';
}
function generateDungeonFloor(){
  DNG.room=0; DNG.maxRooms=4+DNG.floor; DNG.rooms=[];
  var dz=DUNGEON_ZONES[DNG.zone];
  for(var i=0;i<DNG.maxRooms;i++){
    var isBoss=(i===DNG.maxRooms-1);
    var type=isBoss?'boss':DNG_ROOM_POOL[Math.floor(Math.random()*DNG_ROOM_POOL.length)];
    var eid=pick(dz.enemies);
    var eBase=ENEMIES[eid];
    var scaledHp=Math.floor((eBase?eBase.hp:50)*(1+DNG.floor*0.18));
    var boss=isBoss?Object.assign({},DNG_BOSSES[dz.bossPool]||DNG_BOSSES.forest_boss_dng):null;
    if(boss){boss.hp=Math.floor(boss.maxHp*(1+DNG.floor*0.2));boss.maxHp=boss.hp;}
    DNG.rooms.push({type:type,cleared:false,
      enemy:eBase?Object.assign({},eBase,{hp:scaledHp,maxHp:scaledHp}):null,
      bossData:boss});
  }
}
function renderDungeon(){
  var dz=DUNGEON_ZONES[DNG.zone]||{};
  document.getElementById('dng-title').textContent=(dz.icon||'🏰')+' '+dz.name+' — Этаж '+DNG.floor;
  document.getElementById('dng-floor').textContent=DNG.floor;
  document.getElementById('dng-room').textContent=DNG.room+1;
  document.getElementById('dng-room-total').textContent=DNG.maxRooms;
  document.getElementById('dng-hp').textContent=Math.ceil(DNG.hp)+'/'+DNG.maxHp;
  // Progress dots
  var dots=document.getElementById('dng-progress-dots');dots.innerHTML='';
  var typeIcon={boss:'💀',treasure:'📦',rest:'🔥',trap:'⚠',shop_room:'🛒',combat:'⚔'};
  for(var i=0;i<DNG.maxRooms;i++){
    var r=DNG.rooms[i];
    var d=document.createElement('div');
    var col=r.cleared?'#27ae60':(i===DNG.room?'#c9a227':'#2a2540');
    d.style.cssText='width:30px;height:30px;border-radius:6px;background:'+col+';display:flex;align-items:center;justify-content:center;font-size:13px;border:1px solid '+(i===DNG.room?'#c9a227':'#333')+';opacity:'+(i>DNG.room&&!r.cleared?.4:1);
    d.textContent=r.cleared?'✓':(typeIcon[r.type]||'⚔');
    dots.appendChild(d);
  }
  renderDungeonRoom();
}
function renderDungeonRoom(){
  var main=document.getElementById('dng-main');
  var room=DNG.rooms[DNG.room];if(!room){main.innerHTML='';return;}
  var html='';
  if(room.type==='combat'||room.type==='boss'){
    var e=room.type==='boss'?room.bossData:room.enemy;if(!e){dngAdvance();return;}
    var ehp=Math.max(0,Math.ceil(e.hp)),epct=Math.max(0,Math.round(e.hp/e.maxHp*100));
    var php=Math.max(0,Math.ceil(DNG.hp)),ppct=Math.max(0,Math.round(DNG.hp/DNG.maxHp*100));
    html='<div style="background:#0a0a12;border-radius:10px;padding:14px;margin-bottom:10px">'
      +'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
      +'<div style="font-size:42px">'+e.icon+'</div><div style="font-size:26px">⚔</div></div>'
      +'<div style="font-size:14px;font-weight:bold;color:'+(room.type==='boss'?'#e74c3c':'#d4c9a8')+'">'+esc(e.name)+'</div>'
      +'<div style="height:8px;background:#1a1a2e;border-radius:4px;margin:5px 0"><div style="width:'+epct+'%;height:8px;background:#c0392b;border-radius:4px"></div></div>'
      +'<div style="font-size:10px;color:#666">'+ehp+'/'+e.maxHp+' HP</div>'
      +'<div style="height:6px;background:#1a1a2e;border-radius:3px;margin:8px 0 3px"><div style="width:'+ppct+'%;height:6px;background:#27ae60;border-radius:3px"></div></div>'
      +'<div style="font-size:10px;color:#666">Твой HP: '+php+'/'+DNG.maxHp+'</div>'
      +'</div>';
    if(DNG.log.length){
      html+='<div style="background:#050508;border-radius:8px;padding:6px 10px;margin-bottom:8px;max-height:72px;overflow-y:auto;font-size:11px" id="dng-log">'
        +DNG.log.slice(-6).map(function(l){return '<div style="color:'+l.c+'">'+esc(l.t)+'</div>';}).join('')+'</div>';
    }
    if(!room.cleared){
      html+='<div style="display:flex;gap:6px;flex-wrap:wrap">'
        +'<button onclick="dngAttack()" style="flex:1;padding:9px;border-radius:8px;border:none;background:linear-gradient(135deg,#6b1515,#8b2020);color:#ffa0a0;font-size:13px;font-weight:bold;cursor:pointer">⚔ Атака</button>'
        +'<button onclick="dngSkill()" style="flex:1;padding:9px;border-radius:8px;border:none;background:linear-gradient(135deg,#1a2d6b,#1e4d7b);color:#80b0ff;font-size:13px;font-weight:bold;cursor:pointer">🔥 Навык</button>'
        +'<button onclick="dngHeal()" style="flex:1;padding:9px;border-radius:8px;border:none;background:linear-gradient(135deg,#0d3d1a,#1a5c28);color:#80ff90;font-size:13px;font-weight:bold;cursor:pointer">💚 Лечение</button>'
        +'</div>';
    } else {
      html+='<button onclick="dngAdvance()" style="width:100%;padding:10px;border-radius:9px;border:none;background:var(--purple);color:#fff;font-size:13px;font-weight:bold;cursor:pointer">→ Дальше</button>';
    }
  } else if(room.type==='treasure'){
    html='<div style="text-align:center;padding:14px">'
      +'<div style="font-size:48px;margin-bottom:8px">📦</div>'
      +'<div style="font-size:15px;font-weight:bold;color:var(--gold);margin-bottom:6px">Сокровищница!</div>'
      +(room.cleared
        ?'<div style="font-size:12px;color:#27ae60;margin-bottom:10px">✓ Открыт</div><button onclick="dngAdvance()" style="padding:8px 20px;border-radius:8px;border:none;background:var(--purple);color:#fff;font-size:12px;cursor:pointer">→ Дальше</button>'
        :'<button onclick="dngOpenTreasure()" style="padding:10px 24px;border-radius:9px;border:none;background:var(--gold);color:#000;font-size:13px;font-weight:bold;cursor:pointer">Открыть!</button>')
      +'</div>';
  } else if(room.type==='rest'){
    var healAmt=Math.floor(DNG.maxHp*0.35);
    html='<div style="text-align:center;padding:14px">'
      +'<div style="font-size:48px;margin-bottom:8px">🔥</div>'
      +'<div style="font-size:15px;font-weight:bold;color:#27ae60;margin-bottom:6px">Место отдыха</div>'
      +(room.cleared
        ?'<div style="font-size:12px;color:#27ae60;margin-bottom:10px">✓ Отдохнул</div><button onclick="dngAdvance()" style="padding:8px 20px;border-radius:8px;border:none;background:var(--purple);color:#fff;font-size:12px;cursor:pointer">→ Дальше</button>'
        :'<button onclick="dngRest()" style="padding:10px 24px;border-radius:9px;border:none;background:#27ae60;color:#fff;font-size:13px;font-weight:bold;cursor:pointer">Отдохнуть (+'+healAmt+' HP)</button>')
      +'</div>';
  } else if(room.type==='trap'){
    var trapDmg=Math.floor(DNG.maxHp*0.15);
    html='<div style="text-align:center;padding:14px">'
      +'<div style="font-size:48px;margin-bottom:8px">⚠</div>'
      +'<div style="font-size:15px;font-weight:bold;color:#e74c3c;margin-bottom:6px">Ловушка!</div>'
      +(room.cleared
        ?'<div style="font-size:12px;color:#555;margin-bottom:10px">✓ Пройдена</div><button onclick="dngAdvance()" style="padding:8px 20px;border-radius:8px;border:none;background:var(--purple);color:#fff;font-size:12px;cursor:pointer">→ Дальше</button>'
        :'<div style="font-size:12px;color:#666;margin-bottom:10px">Стрелковая ловушка (-'+trapDmg+' HP). Обезвредить? (50%)</div>'
        +'<div style="display:flex;gap:8px;justify-content:center">'
        +'<button onclick="dngTrap(true)" style="padding:9px 16px;border-radius:8px;border:none;background:#1a5c28;color:#fff;font-size:12px;cursor:pointer">🎯 Обезвредить</button>'
        +'<button onclick="dngTrap(false)" style="padding:9px 16px;border-radius:8px;border:none;background:#555;color:#fff;font-size:12px;cursor:pointer">💨 Пробежать</button>'
        +'</div>')
      +'</div>';
  } else if(room.type==='shop_room'){
    html='<div style="text-align:center;padding:14px">'
      +'<div style="font-size:48px;margin-bottom:8px">🛒</div>'
      +'<div style="font-size:15px;font-weight:bold;color:var(--gold);margin-bottom:6px">Торговец</div>'
      +'<div style="font-size:12px;color:#666;margin-bottom:10px">Лечение +50% HP за 80g</div>'
      +'<div style="display:flex;gap:8px;justify-content:center">'
      +'<button onclick="dngBuyHeal()" style="padding:9px 16px;border-radius:8px;border:none;background:#27ae60;color:#fff;font-size:12px;cursor:pointer">💚 Купить (80g)</button>'
      +'<button onclick="dngAdvance()" style="padding:9px 16px;border-radius:8px;border:none;background:#555;color:#fff;font-size:12px;cursor:pointer">Пропустить</button>'
      +'</div></div>';
  }
  main.innerHTML=html;
  var logEl=document.getElementById('dng-log');if(logEl)logEl.scrollTop=logEl.scrollHeight;
}
function dngLog(text,color){DNG.log.push({t:text,c:color||'#888'});}
function dngAttack(){
  var room=DNG.rooms[DNG.room];if(!room||room.cleared)return;
  var e=room.type==='boss'?room.bossData:room.enemy;
  var res=calcDmg(P.atk,e.def||0);e.hp-=res.dmg;
  dngLog((res.crit?'КРИТ! ':'')+'Ты: -'+res.dmg+' HP '+e.name,res.crit?'#ff6b6b':'#ffd166');
  if(e.hp<=0){e.hp=0;dngCombatWin(room);renderDungeon();return;}
  var er=calcDmg(e.atk||10,P.def);DNG.hp-=er.dmg;
  dngLog(e.name+' бьёт: -'+er.dmg+' HP','#e74c3c');
  if(DNG.hp<=0){DNG.hp=0;dngDeath();return;}
  renderDungeon();
}
function dngSkill(){
  var room=DNG.rooms[DNG.room];if(!room||room.cleared)return;
  var e=room.type==='boss'?room.bossData:room.enemy;
  var res=calcDmg(Math.floor(P.atk*1.7),e.def||0);e.hp-=res.dmg;
  dngLog('🔥 Навык: -'+res.dmg+' HP '+e.name,'#e67e22');
  if(e.hp<=0){e.hp=0;dngCombatWin(room);renderDungeon();return;}
  var er=calcDmg(e.atk||10,P.def);DNG.hp-=er.dmg;
  dngLog(e.name+': -'+er.dmg+' HP','#e74c3c');
  if(DNG.hp<=0){DNG.hp=0;dngDeath();return;}
  renderDungeon();
}
function dngHeal(){
  var heal=Math.floor(DNG.maxHp*0.2);DNG.hp=Math.min(DNG.maxHp,DNG.hp+heal);
  dngLog('💚 +'+heal+' HP','#27ae60');
  var room=DNG.rooms[DNG.room];
  if(room&&!room.cleared&&(room.type==='combat'||room.type==='boss')){
    var e=room.type==='boss'?room.bossData:room.enemy;
    var er=calcDmg(e.atk||10,P.def);DNG.hp-=er.dmg;
    dngLog(e.name+' бьёт пока лечишься: -'+er.dmg+' HP','#e74c3c');
    if(DNG.hp<=0){DNG.hp=0;dngDeath();return;}
  }
  renderDungeon();
}
function dngCombatWin(room){
  room.cleared=true;
  var e=room.type==='boss'?room.bossData:room.enemy;
  var g=Math.floor(rnd(e.gold[0],e.gold[1])*getGoldMult());
  P.gold+=g;gainXP(e.xp||50);updateHdr();
  dngLog('Победа! +'+g+'g','#c9a227');
  var loot=tryDrop(e.pool||'pf_common');
  if(loot){var uid=Date.now()+'_d';P.inventory.push({id:loot,uid:uid,ts:Date.now()});invAddOrder.push(uid);dngLog('+'+ITEMS[loot].n,'#c9a227');}
  if(room.type==='boss')dngBossWin();
}
function dngBossWin(){
  dngLog('🏆 БОСС ПОВЕРЖЕН!','#c9a227');
  var dz=DUNGEON_ZONES[DNG.zone];
  setTimeout(function(){
    var main=document.getElementById('dng-main');if(!main)return;
    if(DNG.floor<(dz?dz.floors:3)){
      main.innerHTML+='<div style="margin-top:10px;text-align:center"><div style="color:var(--gold);font-weight:bold;margin-bottom:8px">🎉 Этаж '+DNG.floor+' пройден!</div>'
        +'<div style="display:flex;gap:8px;justify-content:center">'
        +'<button onclick="dngNextFloor()" style="padding:10px 20px;border-radius:9px;border:none;background:linear-gradient(135deg,#c9a227,#e67e22);color:#000;font-size:13px;font-weight:bold;cursor:pointer">⬇ Этаж '+(DNG.floor+1)+'</button>'
        +'<button onclick="closeDungeon()" style="padding:10px 14px;border-radius:9px;border:none;background:#333;color:#aaa;font-size:12px;cursor:pointer">Выйти</button>'
        +'</div></div>';
    } else {
      main.innerHTML+='<div style="margin-top:10px;text-align:center;padding:10px">'
        +'<div style="font-size:18px;color:var(--gold);font-weight:bold">🏆 ПОДЗЕМЕЛЬЕ ПРОЙДЕНО!</div>'
        +'<button onclick="closeDungeon()" style="margin-top:10px;padding:10px 20px;border-radius:9px;border:none;background:var(--gold);color:#000;font-size:13px;font-weight:bold;cursor:pointer">Выйти!</button>'
        +'</div>';
    }
  },200);
}
function dngNextFloor(){DNG.floor++;DNG.log=[];generateDungeonFloor();renderDungeon();toast('Этаж '+DNG.floor+'!','#c9a227');}
function dngAdvance(){
  var room=DNG.rooms[DNG.room];
  if(room&&!room.cleared&&(room.type==='combat'||room.type==='boss')){toast('Сначала победи врага!','#e74c3c');return;}
  if(DNG.room<DNG.maxRooms-1){DNG.room++;renderDungeon();}
}
function dngDeath(){
  dngLog('💀 Ты погиб!','#e74c3c');P.hp=Math.floor(P.maxHp*0.2);DNG.active=false;updateHdr();
  document.getElementById('dng-main').innerHTML='<div style="text-align:center;padding:20px">'
    +'<div style="font-size:48px;margin-bottom:10px">💀</div>'
    +'<div style="font-size:16px;font-weight:bold;color:#e74c3c;margin-bottom:6px">Ты погиб!</div>'
    +'<div style="font-size:12px;color:#555;margin-bottom:14px">Восстановлено 20% HP</div>'
    +'<button onclick="closeDungeon()" style="padding:10px 24px;border-radius:9px;border:none;background:#5c3d8f;color:#fff;font-size:13px;cursor:pointer">Выйти</button></div>';
}
function dngOpenTreasure(){
  var room=DNG.rooms[DNG.room];if(!room||room.cleared)return;room.cleared=true;
  var dz=DUNGEON_ZONES[DNG.zone];
  var lootPool=dz?ENEMIES[pick(dz.enemies)].pool:'pf_uncommon';
  var g=rnd(30,80)*DNG.floor;P.gold+=g;updateHdr();
  dngLog('📦 +'+g+'g','#c9a227');
  var loot=tryDrop(lootPool);
  if(loot){var uid=Date.now()+'_t';P.inventory.push({id:loot,uid:uid,ts:Date.now()});invAddOrder.push(uid);dngLog('+'+ITEMS[loot].n,'#c9a227');}
  renderDungeon();
}
function dngRest(){
  var room=DNG.rooms[DNG.room];if(!room||room.cleared)return;room.cleared=true;
  var h=Math.floor(DNG.maxHp*0.35);DNG.hp=Math.min(DNG.maxHp,DNG.hp+h);
  dngLog('💚 Отдохнул +'+h+' HP','#27ae60');renderDungeon();
}
function dngTrap(tryDisarm){
  var room=DNG.rooms[DNG.room];if(!room||room.cleared)return;room.cleared=true;
  var dmg=Math.floor(DNG.maxHp*0.15);
  if(tryDisarm&&Math.random()<0.5){dngLog('🎯 Обезвредил!','#27ae60');}
  else{DNG.hp=Math.max(1,DNG.hp-dmg);dngLog('⚠ Ловушка! -'+dmg+' HP','#e74c3c');if(DNG.hp<=1){dngDeath();return;}}
  renderDungeon();
}
function dngBuyHeal(){
  if(P.gold<80){toast('Нужно 80g','#e74c3c');return;}
  P.gold-=80;var h=Math.floor(DNG.maxHp*0.5);DNG.hp=Math.min(DNG.maxHp,DNG.hp+h);
  updateHdr();dngLog('🛒 +'+h+' HP','#27ae60');dngAdvance();
}


function updateMapUI(){
  // Lock overlays village
  var locks={cave:3,ruins:7,volcano:12,abyss:20};
  for(var zid in locks){
    var lock=document.getElementById('lock-'+zid);
    if(lock)lock.style.display=P.level<locks[zid]?'block':'none';
  }
  var mtnGate=document.getElementById('lock-mountains-gate');
  if(mtnGate)mtnGate.style.display=P.level<10?'block':'none';
  var mtnBoss=document.getElementById('lock-mountains_boss');
  if(mtnBoss)mtnBoss.style.display=P.level<15?'block':'none';

  // Markers
  var z=ZONES[currentZone];
  var marker=document.getElementById('map-current-marker');
  if(marker){
    if(z&&z.mapLoc==='village'){marker.style.display='block';marker.setAttribute('transform','translate('+z.mapX+','+(z.mapY-20)+')');}
    else{marker.style.display='none';}
  }
  var markerM=document.getElementById('map-current-marker-mtn');
  if(markerM){
    if(z&&z.mapLoc==='mountains'){markerM.style.display='block';markerM.setAttribute('transform','translate('+z.mapX+','+(z.mapY-20)+')');}
    else{markerM.style.display='none';}
  }
  // Zone info
  if(z){
    document.getElementById('zi-icon').textContent=z.icon;
    document.getElementById('zi-name').textContent=z.name;
    document.getElementById('zi-desc').textContent=z.desc;
    var enames=z.enemies.map(function(eid){var e=ENEMIES[eid];return e?e.name+' '+e.icon:'';}).join(', ');
    document.getElementById('zi-enemies').textContent='Враги: '+enames;
  }
}

function selectZone(zid){
  var z=ZONES[zid];if(!z)return;
  if(P.level<z.reqLv){toast('Нужен уровень '+z.reqLv,'#e74c3c');return;}
  currentZone=zid;P.zone=zid;
  checkQuestZone(zid);
  updateMapUI();
  document.getElementById('map-tooltip').style.display='none';
  var zi=document.getElementById('zi-icon'),zn=document.getElementById('zi-name'),zd=document.getElementById('zi-desc'),ze=document.getElementById('zi-enemies');
  if(zi){zi.textContent=z.icon;zn.textContent=z.name;zd.textContent=z.desc;
    var enames=z.enemies.map(function(eid){var e=ENEMIES[eid];return e?e.name+' '+e.icon:'';}).join(', ');
    ze.textContent='Враги: '+enames;}
  toast('Локация: '+z.name,'#3498db');
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

function getEnemySprite(e){
  var sid=e.sprite||'';
  var svg=MONSTER_SPRITES[sid];
  if(svg)return'<div style="width:80px;height:80px;display:inline-block">'+svg+'</div>';
  return'<div style="font-size:60px;line-height:1">'+e.icon+'</div>';
}
function getPlayerSprite(){
  // Simple SVG warrior
  return'<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg" style="width:70px;height:70px">'
    +'<rect x="28" y="44" width="24" height="24" rx="3" fill="#4a3a6a"/>'
    +'<rect x="30" y="46" width="20" height="20" rx="2" fill="#5a4a7a" stroke="#7a6aaa" stroke-width="1"/>'
    +'<ellipse cx="40" cy="29" rx="12" ry="13" fill="#c8956c"/>'
    +'<rect x="30" y="18" width="20" height="12" rx="6" fill="#4a3a6a"/>'
    +'<circle cx="36" cy="28" r="2.5" fill="#333"/><circle cx="44" cy="28" r="2.5" fill="#333"/>'
    +'<circle cx="36" cy="27" r="1" fill="#eee" opacity=".7"/><circle cx="44" cy="27" r="1" fill="#eee" opacity=".7"/>'
    +'<path d="M36 35 Q40 39 44 35" stroke="#a06040" stroke-width="2" fill="none"/>'
    +'<rect x="10" y="42" width="14" height="24" rx="4" fill="#4a3a6a" stroke="#7a6aaa" stroke-width="1"/>'
    +'<rect x="56" y="42" width="14" height="24" rx="4" fill="#4a3a6a" stroke="#7a6aaa" stroke-width="1"/>'
    +'<rect x="30" y="68" width="9" height="10" rx="2" fill="#4a3a6a"/>'
    +'<rect x="41" y="68" width="9" height="10" rx="2" fill="#4a3a6a"/>'
    +'<rect x="58" y="32" width="4" height="32" rx="2" fill="#ccc" stroke="#eee" stroke-width="0.5"/>'
    +'<polygon points="58,32 62,22 66,32" fill="#ddd"/>'
    +'<rect x="8" y="42" width="16" height="3" rx="1" fill="#888"/>'
    +'</svg>';
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
    +'<div style="position:absolute;inset:0;overflow:hidden;pointer-events:none" id="battle-deco-layer"></div>'
    // Player
    +'<div class="player-sprite" id="player-sprite">'
    +'<div class="sprite-body" id="player-body">'+getPlayerSprite()+'</div>'
    +'<div class="sprite-name">'+esc(curUser.nick)+'</div>'
    +'</div>'
    // Enemy
    +'<div class="enemy-sprite" id="enemy-sprite">'
    +'<div class="enemy-body" id="enemy-body">'+getEnemySprite(e)+'</div>'
    +'<div class="sprite-name r-'+(e.rarity||'common')+'">'+esc(e.name)+'</div>'
    +'</div>'
    +'</div>'
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
    +'<div class="battle-log-wrap" id="battle-log"></div>'
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
  var houseMult=getHouseAtkMult();
  base=Math.floor(base*houseMult);
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
  // Pet attack
  var petDmg=petAttack(battle.enemy.def);
  if(petDmg>0){
    battle.enemyHp-=petDmg;
    blogAdd('loot',P.pet.icon+' '+P.pet.name+' атакует: -'+petDmg+' урона!');
    setTimeout(function(){spawnDmgFloat(petDmg,false,false,true);},400);
  }
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

// Где падает этот предмет и с каким шансом
function getDropChances(itemId){
  var results=[];
  var POOL_LABELS={
    pf_common:'Лес (волк/гоблин)',pf_uncommon:'Лес (разбойник)',
    pc_common:'Пещера (скелет/паук/летучая мышь)',pc_rare:'Пещера (голем/маг)',
    pr_common:'Руины (зомби)',pr_rare:'Руины (голем/маг)',
    pv_uncommon:'Вулкан (элем./тролль)',pv_rare:'Вулкан (дракончик)',
    pa_rare:'Бездна (демон)',pa_epic:'Бездна (лич/рыцарь)',
    pm_common:'Горы (тролль/волк/страж)',pm_rare:'Горы (дракон/гарпия/маг)',
  };
  for(var poolKey in ITEM_POOLS){
    var pool=ITEM_POOLS[poolKey];
    var total=pool.reduce(function(s,x){return s+x.w;},0);
    var entry=pool.find(function(x){return x.id===itemId;});
    if(entry){
      var pct=(entry.w/total*100).toFixed(1);
      var label=POOL_LABELS[poolKey]||poolKey;
      // Global drop chance is 38%
      var effective=(entry.w/total*38).toFixed(1);
      results.push({label:label,pct:pct,effective:effective});
    }
  }
  return results;
}

function openItemModal(uid){
  var entry=P.inventory.find(function(x){return x.uid===uid||x.id===uid;});
  if(!entry){for(var s in P.equipped){if(P.equipped[s]===uid){entry={id:uid,uid:uid};break;}}}
  if(!entry)return;
  var item=ITEMS[entry.id];if(!item)return;
  var isEq=isEquipped(entry.id);
  var sameIdCount=P.inventory.filter(function(x){return x.id===entry.id;}).length;
  var thisIsEquipped=isEq;

  // Drop chances
  var chances=getDropChances(entry.id);
  var chancesHtml='';
  if(chances.length){
    chancesHtml='<div style="margin:8px 0;padding:8px 10px;background:#0a0a10;border-radius:8px;border:1px solid #1a1a2e">'
      +'<div style="font-size:9px;color:#555;text-transform:uppercase;letter-spacing:.06em;margin-bottom:5px">📍 Где падает</div>'
      +chances.map(function(c){
        return '<div style="display:flex;justify-content:space-between;align-items:center;padding:2px 0;font-size:10px">'
          +'<span style="color:#888">'+esc(c.label)+'</span>'
          +'<span style="color:var(--gold);font-weight:bold">'+c.effective+'%</span>'
          +'</div>';
      }).join('')
      +'<div style="font-size:9px;color:#333;margin-top:4px">* шанс за убийство (глоб. 38% × шанс в пуле)</div>'
      +'</div>';
  }

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
    +chancesHtml
    +'<div class="imodal-btns">'
    +(isEq
      ?'<button class="imbtn-eq" onclick="unequipItem(\''+entry.uid+'\',\''+entry.id+'\')">Снять</button>'
      :'<button class="imbtn-eq" onclick="equipItem(\''+entry.uid+'\',\''+entry.id+'\')">Надеть</button>')
    +(thisIsEquipped&&sameIdCount===1
      ?'<button class="imbtn-sell" style="background:linear-gradient(135deg,#5c1a1a,#7c2020)" onclick="sellEquippedItem(\''+entry.uid+'\')">⚠ Продать (надет) '+item.sell+'g</button>'
      :'<button class="imbtn-sell" onclick="sellItem(\''+entry.uid+'\')">Продать ('+item.sell+'g)</button>')
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
  var entry=P.inventory[idx];
  var item=ITEMS[entry.id];if(!item)return;
  // Only unequip if this is the item being sold AND there are no other copies left in inventory
  var otherCopies=P.inventory.filter(function(x,i){return i!==idx&&x.id===entry.id;});
  if(otherCopies.length===0){
    // No other copies — safe to unequip if this item type is equipped
    for(var s in P.equipped){if(P.equipped[s]===entry.id)P.equipped[s]=null;}
  }
  P.gold+=item.sell;
  P.inventory.splice(idx,1);
  recalcStats();updateEquipSlots();updateInvGrid();updateInvStats();updateHdr();closeItemModal();
  toast('+'+item.sell+' золота','#c9a227');
  if(curTab==='shop')document.getElementById('shop-gold').textContent=fmt(P.gold);
}

function sellEquippedItem(uid){
  // Unequip first, then sell
  var entry=P.inventory.find(function(x){return x.uid===uid;});
  if(!entry)return;
  var item=ITEMS[entry.id];if(!item)return;
  if(!confirm('Продать надетый предмет «'+item.n+'» за '+item.sell+' золота?'))return;
  for(var s in P.equipped){if(P.equipped[s]===entry.id)P.equipped[s]=null;}
  P.gold+=item.sell;
  var idx=P.inventory.findIndex(function(x){return x.uid===uid;});
  if(idx!==-1)P.inventory.splice(idx,1);
  recalcStats();updateEquipSlots();updateInvGrid();updateInvStats();updateHdr();closeItemModal();
  toast('Снято и продано: +'+item.sell+' золота','#c9a227');
  if(curTab==='shop')document.getElementById('shop-gold').textContent=fmt(P.gold);
}

function sellAllUnequipped(){
  var toSell=P.inventory.filter(function(e){return !isEquipped(e.id);});
  if(!toSell.length){toast('Нечего продавать','#555');return;}
  var total=toSell.reduce(function(s,e){var it=ITEMS[e.id];return s+(it?it.sell:0);},0);
  if(!confirm('Продать '+toSell.length+' ненадетых предметов за '+total+' золота?'))return;
  var uids=toSell.map(function(e){return e.uid;});
  P.inventory=P.inventory.filter(function(e){return uids.indexOf(e.uid)===-1;});
  P.gold+=total;
  recalcStats();updateEquipSlots();updateInvGrid();updateInvStats();updateHdr();
  toast('Продано '+toSell.length+' предметов! +'+total+' золота','#c9a227');
  if(curTab==='shop')document.getElementById('shop-gold').textContent=fmt(P.gold);
}
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
      +'<button class="case-open-btn" onclick="openCase(\''+c.id+'\')">Открыть</button>';
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
        +'<button onclick="joinRaid(\'+r.raid_id+\')" style="padding:6px 12px;border-radius:7px;border:none;background:#5c3d8f;color:#fff;font-size:12px;cursor:pointer">Войти</button>';
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
    if(data.requests&&data.requests.length){reqBox.innerHTML='';data.requests.forEach(function(r){var row=document.createElement('div');row.className='req-row';row.innerHTML='<span class="req-nick">'+esc(r.nick)+' ('+esc(r.login)+')</span><button class="req-btn acc" onclick="answerReq(\''+esc(r.login)+'\',true)">Принять</button><button class="req-btn dec" onclick="answerReq(\''+esc(r.login)+'\',false)">Отклонить</button>';reqBox.appendChild(row);});}
    else reqBox.innerHTML='<div style="color:#444;font-size:13px">Нет заявок</div>';
    var fBox=document.getElementById('friend-list'),sel=document.getElementById('transfer-to'),prev=sel.value;
    sel.innerHTML='<option value="">-- выбери друга --</option>';
    if(data.friends&&data.friends.length){fBox.innerHTML='';data.friends.forEach(function(f){var frow=document.createElement('div');frow.className='friend-row';frow.innerHTML='<div><div class="friend-nick">'+esc(f.nick)+'</div><div class="friend-info">Золото: '+fmt(f.earned||0)+'</div></div><button class="fbtn2 red" onclick="removeFriend(\''+esc(f.login)+'\')">Удалить</button>';fBox.appendChild(frow);var opt=document.createElement('option');opt.value=f.login;opt.textContent=f.nick;sel.appendChild(opt);});if(prev)sel.value=prev;}
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
    if len(data.login.strip()) < 3:
        raise HTTPException(400, "Логин слишком короткий (мин. 3 символа)")
    if len(data.password) < 3:
        raise HTTPException(400, "Пароль слишком короткий (мин. 3 символа)")
    if len(data.nick.strip()) < 2:
        raise HTTPException(400, "Никнейм слишком короткий (мин. 2 символа)")
    login = data.login.lower().strip()
    nick = data.nick.strip()
    ph = hash_pass(data.password, login)
    conn = db()
    try:
        existing = conn.execute("SELECT id FROM users WHERE login=?", (login,)).fetchone()
        if existing:
            raise HTTPException(400, "Такой логин уже занят")
        conn.execute(
            "INSERT INTO users (login,nick,passhash,created,game_data) VALUES (?,?,?,?,?)",
            (login, nick, ph, int(time.time()*1000), "{}")
        )
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "nick": nick, "passhash": ph, "login": login, "game_data": {}}

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

        # Count members for damage bonus (+8% per additional member)
        member_total = conn.execute("SELECT COUNT(*) as cnt FROM raid_members WHERE raid_id=?", (data.raid_id,)).fetchone()["cnt"]
        member_bonus = 1.0 + max(0, member_total - 1) * 0.08

        # Player attacks boss
        atk_val = member["atk"] * (1.6 if data.skill else 1.0) * member_bonus
        dmg = max(1, int(atk_val - boss_def * 0.5) + random.randint(-3, 3))
        is_crit = random.random() < 0.15
        if is_crit:
            dmg = int(dmg * 1.8)
        boss_hp -= dmg

        bonus_txt = f" (+{round((member_bonus-1)*100)}% за {member_total} уч.)" if member_total > 1 else ""
        action_desc = ("КРИТ! " if is_crit else "") + f"{member['nick']} {'навык' if data.skill else 'атакует'}: -{dmg} HP боссу{bonus_txt}"
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
