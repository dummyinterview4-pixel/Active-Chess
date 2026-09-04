import { useEffect, useMemo, useState } from 'react';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';
import { useBoardWidth } from './useBoardWidth';

const SQUARE_LIGHT = '#E7D9BB';
const SQUARE_DARK = '#8A6B4B';
const SELECTED_SQUARE = 'rgba(231, 196, 118, 0.70)';
const TARGET_DOT = 'radial-gradient(circle, rgba(85, 207, 160, 0.75) 24%, transparent 26%)';

/**
 * A real, rules-legal chessboard for puzzle attempts.
 *
 * This component only knows how to (a) show a position and (b) let the
 * student make a *legal* move on it — chess.js is the referee for what's
 * draggable/clickable. It does NOT know whether a move is the *correct*
 * puzzle solution: puzzle answers are never sent to the client (see
 * PuzzleOut on the backend), so the resulting SAN move is handed to the
 * parent via `onMove`, which submits it to `/puzzles/{id}/attempt` — the
 * backend remains the sole authority on correctness.
 *
 * `fen` is the puzzle's starting position and stays constant while a puzzle
 * is active; this board keeps its own `displayFen` so a played move is
 * visible immediately, and reverts to `fen` whenever `resetKey` changes
 * (the parent bumps it after a wrong attempt) or a new puzzle's `fen` comes
 * in.
 */
export default function PuzzleChessBoard({ fen, locked, onMove, resetKey }) {
  const [wrapRef, boardWidth] = useBoardWidth(420);
  const [displayFen, setDisplayFen] = useState(fen);
  const [selectedSquare, setSelectedSquare] = useState(null);

  const orientation = fen.split(' ')[1] === 'b' ? 'black' : 'white';
  const myColor = orientation === 'white' ? 'w' : 'b';

  useEffect(() => {
    setDisplayFen(fen);
    setSelectedSquare(null);
  }, [fen, resetKey]);

  const legalTargets = useMemo(() => {
    if (!selectedSquare) return [];
    try {
      const c = new Chess(displayFen);
      return c.moves({ square: selectedSquare, verbose: true }).map((m) => m.to);
    } catch {
      return [];
    }
  }, [selectedSquare, displayFen]);

  function tryMove(from, to) {
    if (locked) return false;
    try {
      const c = new Chess(displayFen);
      const move = c.move({ from, to, promotion: 'q' });
      if (!move) return false;
      setDisplayFen(c.fen());
      setSelectedSquare(null);
      onMove(move.san);
      return true;
    } catch {
      return false;
    }
  }

  function onDrop(from, to) {
    return tryMove(from, to);
  }

  function onSquareClick(square) {
    if (locked) return;
    if (!selectedSquare) {
      try {
        const c = new Chess(displayFen);
        const piece = c.get(square);
        if (piece && piece.color === myColor) setSelectedSquare(square);
      } catch {
        // ignore — leave selection as-is
      }
      return;
    }
    if (selectedSquare === square) {
      setSelectedSquare(null);
      return;
    }
    try {
      const c = new Chess(displayFen);
      const piece = c.get(square);
      if (piece && piece.color === myColor) {
        setSelectedSquare(square);
        return;
      }
    } catch {
      // fall through to a move attempt
    }
    tryMove(selectedSquare, square);
  }

  const customSquareStyles = useMemo(() => {
    const styles = {};
    if (selectedSquare) {
      styles[selectedSquare] = { background: SELECTED_SQUARE, boxShadow: 'inset 0 0 10px rgba(0,0,0,0.3)' };
      legalTargets.forEach((sq) => {
        styles[sq] = { background: TARGET_DOT, borderRadius: '50%' };
      });
    }
    return styles;
  }, [selectedSquare, legalTargets]);

  return (
    <div className="puzzle-board-canvas" ref={wrapRef}>
      <Chessboard
        position={displayFen}
        onPieceDrop={onDrop}
        onSquareClick={onSquareClick}
        boardOrientation={orientation}
        boardWidth={boardWidth}
        arePiecesDraggable={!locked}
        animationDuration={200}
        customDarkSquareStyle={{ backgroundColor: SQUARE_DARK }}
        customLightSquareStyle={{ backgroundColor: SQUARE_LIGHT }}
        customBoardStyle={{ borderRadius: '14px', boxShadow: '0 8px 24px rgba(0,0,0,0.18)' }}
        customSquareStyles={customSquareStyles}
      />
    </div>
  );
}
