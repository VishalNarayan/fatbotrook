import sys
import chess
from fatbotrook import FatBotEngine






def main():
	while True:
		fen = input("Enter FEN string: ")
		if fen == "":
			exit(0)

		
		try:
			board = chess.Board(fen)
			fbe = FatBotEngine(4)

			move = fbe.search(board)

			print(f"FATBOT found move: {move}")

		except:
			print("Invalid FEN!")
		



if __name__ == "__main__":
	'''
	args = sys.argv[1:]
	if len(args) < 1:
		print("Invalid args", file=sys.stderr)
		exit(1)
	'''
	main()