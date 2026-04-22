import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const rootDir = path.join(process.cwd(), '..');
    const statePath = path.join(rootDir, 'data/paper_state.json');
    const logPath = path.join(rootDir, 'heartbeat.log');

    // 1. Читаем баланс
    let state = { balance: 100.0, positions: [], history: [] };
    if (fs.existsSync(statePath)) {
      state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
    }

    // 2. Читаем последние логи (последние 30 строк)
    let logs: string[] = [];
    if (fs.existsSync(logPath)) {
      const allLogs = fs.readFileSync(logPath, 'utf8').split('\n').filter(Boolean);
      logs = allLogs.slice(-30);
    }

    // 3. Читаем состояние рынка
    const marketPath = path.join(rootDir, 'data/market_state.json');
    let market = null;
    if (fs.existsSync(marketPath)) {
      try {
        market = JSON.parse(fs.readFileSync(marketPath, 'utf8'));
      } catch (e) {}
    }

    const pausePath = path.join(rootDir, 'data/pause.flag');
    const isPaused = fs.existsSync(pausePath);

    return NextResponse.json({
      success: true,
      balance: state.balance,
      activePositions: state.positions.length,
      positions: state.positions,
      historyCount: state.history.length,
      history: state.history,
      market: market,
      logs: logs,
      isPaused: isPaused,
      lastUpdate: new Date().toISOString()
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
