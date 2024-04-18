#lang forge/temporal


abstract sig Num {}
one sig One, Two, Three, Four, Five, Six, Seven, Eight, Nine extends Num {}
one sig Board {
    var board: pfunc Num -> Num -> Num
}

fun digits: one set {1 + 2 + 3}

pred wellformed {
    // all row: Num | all disj c1, c2: Num {
    //     some Board.board[row][c1] implies (Board.board[row][c1] != Board.board[row][c2])
    // }

    // all col: Num | all disj r1, r2: Num {
    //     some Board.board[r1][col] implies (Board.board[r1][col] != Board.board[r2][col])
    // }

    // all col: digits & Int | {
    //     Board.board[1][col] = Two
    // }

    // all n: Num | {
    //     some r, c: Num | Board.board[r][c] = n
    // }
}

run {
    wellformed
}