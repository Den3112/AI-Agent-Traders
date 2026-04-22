"use client";

import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Play, Pause, RefreshCw, Activity, Terminal, ShieldAlert, Cpu, RotateCcw, Trash2 } from 'lucide-react';

export default function Dashboard() {
  const [mounted, setMounted] = useState(false);
  const [loadingAction, setLoadingAction] = useState(false);
  const [data, setData] = useState({
    balance: 100.0,
    activePositions: 0,
    positions: [] as any[],
    historyCount: 0,
    history: [] as any[],
    market: null as any,
    isPaused: false,
    logs: [] as string[]
  });

  // Derived metrics
  let currentBal = 100.0;
  const chartData = data.history.length > 0 ? data.history.map((t, idx) => {
    currentBal += (t.pnl || 0);
    return { name: `Trade ${idx+1}`, value: currentBal };
  }) : [{ name: 'Start', value: 100.0 }, { name: 'Now', value: 100.0 }];

  const profitLoss = data.balance - 100;
  const profitPercentage = ((profitLoss) / 100) * 100;
  const isProfitable = profitLoss >= 0;

  useEffect(() => {
    setMounted(true);
    const fetchData = async () => {
      try {
        const res = await fetch('/api/status');
        const json = await res.json();
        if (json.success) setData(json);
      } catch (err) {
        console.error("Fetch failed", err);
      }
    };
    fetchData(); 
    const interval = setInterval(fetchData, 3000); 
    return () => clearInterval(interval);
  }, []);

  const handleControl = async (action: string) => {
    setLoadingAction(true);
    try {
      const resp = await fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      });
      const result = await resp.json();
      if (result.success) {
        if (action === 'pause') setData(prev => ({...prev, isPaused: true}));
        if (action === 'resume') setData(prev => ({...prev, isPaused: false}));
      }
    } catch (error: any) {
      console.error('Action failed:', error);
    }
    setTimeout(() => setLoadingAction(false), 800);
  };

  if (!mounted) return null;

  const scannerData = data.market?.scanner || [];
  const bestSignal = data.market?.best_signal?.symbol;
  const marketVolatility = data.market?.market_volatility || 0;
  const isAutoKilled = marketVolatility > 5.0;

  return (
    <main className="min-h-screen p-4 sm:p-8 md:p-12 max-w-[1600px] mx-auto text-zinc-300 font-sans tracking-tight">
      {/* Header section with Linear-esque minimalism */}
      <header className="flex flex-col md:flex-row justify-between md:items-end gap-6 mb-10 border-b border-zinc-800 pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center border border-zinc-700">
              <Cpu className="w-4 h-4 text-zinc-100" />
            </div>
            <h1 className="text-xl sm:text-2xl font-semibold text-zinc-100 tracking-tight">Autonomous Trading Engine</h1>
          </div>
          <p className="text-sm text-zinc-500 font-medium">Multi-Agent System • Market State: {data.isPaused ? 'Manual Halt' : isAutoKilled ? 'Auto-Killed (High Volatility)' : 'Monitoring'}</p>
        </div>
        
        <div className="flex flex-wrap items-center gap-3 text-xs font-mono">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-md bg-zinc-900 border ${isAutoKilled ? 'border-amber-500/50' : 'border-zinc-800'}`}>
            <span className={`w-2 h-2 rounded-full ${data.isPaused ? 'bg-zinc-500' : isAutoKilled ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500 animate-pulse'}`}></span>
            <span className="text-zinc-400">Volatility Index: <span className={isAutoKilled ? "text-amber-400 font-bold" : "text-zinc-100"}>{marketVolatility.toFixed(2)}%</span></span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-zinc-900 border border-zinc-800">
            <span className="text-zinc-400">Environment: <span className="text-zinc-100">Paper Trading</span></span>
          </div>
          <a 
            href="http://127.0.0.1:18789/dashboard/chat?session=main#token=admin123" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 transition-colors text-zinc-400"
          >
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-zinc-100">Live Chat</span>
          </a>
          <a 
            href="http://localhost:18789/__openclaw__/canvas/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 transition-colors text-zinc-400"
          >
            <Activity className="w-3.5 h-3.5 text-blue-400" />
            <span className="text-zinc-100">Agent Map</span>
          </a>
        </div>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        
        {/* Left Column (Main Content) */}
        <div className="xl:col-span-8 flex flex-col gap-6">
          
          {/* Equity Chart */}
          <div className="premium-card p-6 h-[400px] flex flex-col">
            <div className="flex justify-between items-start mb-8">
              <div>
                <h2 className="text-sm font-medium text-zinc-400 mb-1">Total Equity</h2>
                <div className="flex items-baseline gap-3">
                  <span className="text-4xl font-semibold text-zinc-100 font-mono tracking-tight">${data.balance.toFixed(2)}</span>
                  <span className={`text-sm font-medium flex items-center px-2 py-0.5 rounded-md ${isProfitable ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                    {isProfitable ? '+' : ''}{profitLoss.toFixed(2)} ({profitPercentage.toFixed(2)}%)
                  </span>
                </div>
              </div>
              <div className="flex gap-8 text-right">
                <div>
                  <p className="text-xs font-medium text-zinc-500 mb-1 text-left">Executions</p>
                  <p className="text-xl font-medium text-zinc-100 font-mono">{data.historyCount}</p>
                </div>
              </div>
            </div>
            
            <div className="flex-1 w-full -ml-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.2}/>
                      <stop offset="100%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="name" hide />
                  <YAxis domain={['dataMin - 5', 'dataMax + 5']} hide />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '8px', color: '#e4e4e7', fontSize: '12px' }}
                    itemStyle={{ color: '#60a5fa' }}
                    labelStyle={{ color: '#a1a1aa', marginBottom: '4px' }}
                  />
                  <Area type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} fill="url(#equityGradient)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Active Trades */}
            <div className="premium-card p-6 flex flex-col min-h-[300px]">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-sm font-medium text-zinc-100 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-zinc-400" /> Active Positions
                </h2>
                <span className="badge bg-zinc-800 border-zinc-700 text-zinc-300">{data.positions.length}</span>
              </div>
              
              <div className="flex-1 overflow-y-auto space-y-3">
                {data.positions.length === 0 ? (
                  <div className="h-full flex items-center justify-center text-zinc-500 text-sm">
                    No active positions.
                  </div>
                ) : (
                  data.positions.map((pos: any, i: number) => (
                    <div key={i} className="group p-4 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-zinc-700 transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-sm text-zinc-100">{pos.symbol}</span>
                          <span className={`badge ${pos.side === 'buy' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
                            {pos.side.toUpperCase()}
                          </span>
                        </div>
                        <span className="font-mono text-sm text-zinc-300">
                          ${pos.entry_price.toFixed(2)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center mt-3 pt-3 border-t border-zinc-800">
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] uppercase text-zinc-500 font-semibold">T/P</span>
                          <span className="text-xs font-mono text-emerald-400/80">${pos.take_profit.toFixed(2)}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] uppercase text-zinc-500 font-semibold">S/L</span>
                          <span className="text-xs font-mono text-red-400/80">${pos.stop_loss.toFixed(2)}</span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Control Center */}
            <div className="premium-card p-6 flex flex-col">
              <h2 className="text-sm font-medium text-zinc-100 flex items-center gap-2 mb-6">
                <ShieldAlert className="w-4 h-4 text-zinc-400" /> Command Interface
              </h2>
              
              <div className="space-y-4">
                <button 
                  onClick={() => handleControl(data.isPaused ? 'resume' : 'pause')}
                  disabled={loadingAction}
                  className={`w-full py-2.5 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2
                    ${data.isPaused 
                      ? 'bg-zinc-100 text-zinc-900 hover:bg-white' 
                      : 'bg-zinc-900 border border-red-900/50 text-red-500 hover:bg-red-950/30 hover:border-red-500/30'
                    } disabled:opacity-50`}
                >
                  {data.isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                  {data.isPaused ? 'Resume Execution' : 'Halt Trading (Killswitch)'}
                </button>
                
                <button 
                  onClick={() => handleControl('force_scan')}
                  disabled={loadingAction}
                  className="w-full py-2.5 rounded-lg text-sm font-medium bg-zinc-900 border border-zinc-800 text-zinc-300 hover:bg-zinc-800 transition-colors flex items-center justify-center gap-2"
                >
                  <RefreshCw className={`w-4 h-4 ${loadingAction ? 'animate-spin' : ''}`} />
                  Trigger Force Scan
                </button>
              </div>

              <div className="mt-8 pt-6 border-t border-zinc-800 flex-1">
                <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-4">Agent Subsystem Status</h3>
                <div className="space-y-3">
                  {[
                    { name: 'Lead Coordinator', status: 'Online', color: 'text-zinc-300', pulse: true },
                    { name: 'Market Analyst', status: data.isPaused ? 'Halted' : 'Active', color: data.isPaused ? 'text-zinc-600' : 'text-blue-400' },
                    { name: 'Execution Engine', status: data.positions.length > 0 ? 'Managing' : 'Idle', color: data.positions.length > 0 ? 'text-amber-400' : 'text-zinc-600' },
                  ].map((agent, idx) => (
                    <div key={idx} className="flex justify-between items-center text-sm">
                      <span className="text-zinc-400 flex items-center gap-2">
                        {agent.pulse && (
                          <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                          </span>
                        )}
                        {agent.name}
                      </span>
                      <span className={`font-medium ${agent.color}`}>{agent.status}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="xl:col-span-4 flex flex-col gap-6">
          
          {/* Market Radar */}
          <div className="premium-card flex flex-col h-[400px]">
             <div className="p-5 border-b border-zinc-800 flex justify-between items-center bg-zinc-900/50 rounded-t-xl">
               <h2 className="text-sm font-medium text-zinc-100 flex items-center gap-2">
                 Scanner Heatmap
               </h2>
             </div>
             
             <div className="flex-1 overflow-y-auto p-2">
               <table className="w-full text-sm text-left">
                 <thead className="text-xs text-zinc-500 sticky top-0 bg-[#121214]/90 backdrop-blur-md z-10">
                   <tr>
                     <th className="px-4 py-3 font-medium">Asset</th>
                     <th className="px-4 py-3 font-medium text-right">RSI(14)</th>
                     <th className="px-4 py-3 font-medium text-right">Trend</th>
                   </tr>
                 </thead>
                 <tbody className="divide-y divide-zinc-800/50">
                    {scannerData.length === 0 ? (
                      <tr>
                        <td colSpan={3} className="px-4 py-8 text-center text-zinc-600">Awaiting scan cycle...</td>
                      </tr>
                    ) : (
                      scannerData.map((coin: any, i: number) => {
                        const isOversold = coin.rsi < 35;
                        const isOverbought = coin.rsi > 65;
                        const isBest = coin.symbol === bestSignal;
                        
                        return (
                          <tr key={i} className={`group ${isBest ? 'bg-zinc-800/20' : 'hover:bg-zinc-900/30'} transition-colors`}>
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-2">
                                <span className={`w-1.5 h-1.5 rounded-full ${isBest ? 'bg-blue-500' : 'bg-transparent'}`}></span>
                                <span className="font-mono text-zinc-200">{coin.symbol.replace('/USDT', '')}</span>
                              </div>
                            </td>
                            <td className="px-4 py-3 text-right">
                              <span className={`font-mono text-xs px-2 py-0.5 rounded-md
                                ${isOversold ? 'bg-emerald-500/10 text-emerald-400' : 
                                  isOverbought ? 'bg-red-500/10 text-red-400' : 'text-zinc-400'}
                              `}>
                                {coin.rsi.toFixed(1)}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-right">
                              <span className="text-xs text-zinc-500 tracking-wide uppercase">{coin.trend}</span>
                            </td>
                          </tr>
                        );
                      })
                    )}
                 </tbody>
               </table>
             </div>
          </div>

          {/* Farm Management */}
          <div className="premium-card flex flex-col">
            <div className="p-4 border-b border-zinc-800 flex items-center gap-2 bg-zinc-900/50 rounded-t-xl">
              <Cpu className="w-4 h-4 text-zinc-400" />
              <h2 className="text-sm font-medium text-zinc-100">Farm Management</h2>
            </div>
            
            <div className="p-5 space-y-3">
              <button 
                onClick={() => handleControl('restart_ai')}
                disabled={loadingAction}
                className="w-full py-2 text-xs font-medium bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white hover:border-zinc-500 transition-all rounded-md flex items-center justify-center gap-2 shadow-sm"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Restart AI Engine (OpenClaw)
              </button>
              
              <button 
                onClick={() => handleControl('clear_history')}
                disabled={loadingAction}
                className="w-full py-2 text-xs font-medium bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-red-400 hover:border-red-900/50 transition-all rounded-md flex items-center justify-center gap-2 shadow-sm"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Flush Execution History
              </button>

              <div className="pt-2 text-[10px] text-zinc-600 text-center uppercase tracking-widest font-bold opacity-50">
                Host: Ubuntu 24.04-LTS (WSL)
              </div>
            </div>
          </div>

          {/* Terminal / Logs */}
          <div className="premium-card flex flex-col flex-1 min-h-[300px]">
            <div className="p-4 border-b border-zinc-800 flex items-center gap-2 bg-zinc-900/50 rounded-t-xl">
              <Terminal className="w-4 h-4 text-zinc-400" />
              <h2 className="text-sm font-medium text-zinc-100">System Logs</h2>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 bg-[#0a0a0b] rounded-b-xl border-t border-transparent shadow-inner">
              <div className="font-mono text-[11px] leading-relaxed break-words space-y-1.5">
                {data.logs.length === 0 ? (
                  <p className="text-zinc-600 animate-pulse">Connecting to stream...</p>
                ) : (
                  data.logs.map((log, i) => {
                    let colorClass = "text-zinc-500";
                    if (log.includes("[ERROR]") || log.includes("failed")) colorClass = "text-red-400";
                    else if (log.includes("[INFO]")) colorClass = "text-zinc-400";
                    else if (log.includes("detected") || log.includes("Best setup")) colorClass = "text-emerald-400";
                    else if (log.includes("OPENED") || log.includes("PLACED")) colorClass = "text-blue-400";
                    else if (log.includes("ALERT")) colorClass = "text-amber-400";
                    
                    return (
                      <div key={i} className={`flex gap-2 ${colorClass}`}>
                        <span className="text-zinc-700 select-none">›</span>
                        <span className="flex-1">{log}</span>
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>

        </div>
      </div>
    </main>
  );
}
