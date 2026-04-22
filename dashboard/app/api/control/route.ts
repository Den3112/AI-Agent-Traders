import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';

export async function POST(req: Request) {
  try {
    const { action } = await req.json();
    const rootDir = path.join(process.cwd(), '..');
    const pausePath = path.join(rootDir, 'data/pause.flag');

    if (action === 'pause') {
      fs.writeFileSync(pausePath, 'PAUSED', 'utf-8');
      return NextResponse.json({ success: true, message: "System paused." });
    } 
    else if (action === 'resume') {
      if (fs.existsSync(pausePath)) {
        fs.unlinkSync(pausePath);
      }
      return NextResponse.json({ success: true, message: "System resumed." });
    }
    else if (action === 'force_scan') {
      exec('sudo kill $(pgrep -f "scripts/ai/continuous_loop.py") || true && nohup uv run python3 scripts/ai/continuous_loop.py > heartbeat_stdout.log 2>&1 &', { cwd: rootDir });
      return NextResponse.json({ success: true, message: "Forcing manual scan loop restart." });
    }
    else if (action === 'restart_ai') {
      // Перезапуск OpenClaw через системный скрипт
      exec('bash scripts/infra/start_openclaw.sh', { cwd: rootDir });
      return NextResponse.json({ success: true, message: "AI Engine (OpenClaw) restart triggered." });
    }
    else if (action === 'clear_history') {
      const statePath = path.join(rootDir, 'data/paper_state.json');
      if (fs.existsSync(statePath)) {
        const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
        state.history = [];
        fs.writeFileSync(statePath, JSON.stringify(state, null, 2), 'utf-8');
      }
      return NextResponse.json({ success: true, message: "Transaction history cleared." });
    }

    return NextResponse.json({ success: false, error: "Invalid action" }, { status: 400 });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
