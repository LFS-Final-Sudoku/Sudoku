#lang forge/temporal


abstract sig Digit {
    value: Int
}

fun MIN: one Int { 1 }
fun MAX: one Int { 4 }
fun INCREMENT: one Int { 2 }
fun VALUES: one set Int { 1 + 2 + 3 + 4 }
fun VALUES: one set Int { 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 }


one sig Board {
    var board: pfunc Int -> Int -> Int
}

pred wellformed {
    all row, col: Int | {
        // No out of bounds entries
        (row not in VALUES or col not in VALUES) implies no Board.board[row][col]

        // Every entry is a valid value
        some Board.board[row][col] implies Board.board[row][col] in VALUES
    }
}

fun grid_segment[row : Int, col : Int]: Int {
    add[multiply[divide[subtract[row,1], INCREMENT],INCREMENT], add[divide[subtract[col,1], INCREMENT], 1]]
}

pred valid_board {
    // Same column values can't be the same
    all col : Int | all disj row1, row2 : Int | {
        (col in VALUES and row1 in VALUES and row2 in VALUES) implies {
            (some Board.board[row1][col] and some Board.board[row2][col]) implies {
                Board.board[row1][col] != Board.board[row2][col]
            }
        }
    }

    // Same row values can't be the same
    all row : Int | all disj col1, col2 : Int | {
        (row in VALUES and col1 in VALUES and col2 in VALUES) implies {
            (some Board.board[row][col1] and some Board.board[row][col2]) implies {
                Board.board[row][col1] != Board.board[row][col2]
            }
        }
    }

    // Same grid segment values can't be the same
    // all row1, row2, col1, col2 : Int | {
    //     (row1 in VALUES and row2 in VALUES and col1 in VALUES and col2 in VALUES) implies {
    //         (not (row1 = row2 and col1 = col2)) implies {
    //             grid_segment[row1,col1] = grid_segment[row2,col2] implies {
    //                 Board.board[row1][col1] != Board.board[row2][col2]
    //             }
    //         }
    //     }
    // }
}

run { wellformed valid_board } for 5 Int