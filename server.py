import random
import hashlib
import sympy

BITS = 77


def deterministic_word_to_prime(word):
    """Deterministic function that obtains a prime number from a word"""

    def word_to_hash(word):
        # Convert the word to a hash value using SHA-256
        return hashlib.sha256(word.encode()).hexdigest()

    def hash_to_number(hash):
        # Convert the hash string to a bas16 hexadecimal number
        return int(hash, 16)

    def number_to_prime(num):
        # Find the next prime number greater than the given number
        return sympy.nextprime(num)

    # Convert word to hash
    hash = word_to_hash(word)

    # Convert hash to number
    number = hash_to_number(hash)

    # Find next prime
    prime = number_to_prime(number)

    return prime


def random_bits_to_prime(bits):
    """Random function that obtains a prime from bits"""

    while True:
        candidate = random.getrandbits(bits)
        candidate |= (1 << bits - 1) | 1
        if sympy.isprime(candidate):
            return candidate


from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/proof", methods=["GET"])
def create_proof():
    # Read a word and create a proof
    word = request.args.get("word")
    prime_private_word = deterministic_word_to_prime(word)
    proof = random_bits_to_prime(BITS) * prime_private_word
    return jsonify({"proof": str(proof)})


@app.route("/verify", methods=["GET"])
def create_verify():
    # Read a proof and a word and verify the proof
    proof = int(request.args.get("proof"))
    word = request.args.get("word")
    prime_private_word = deterministic_word_to_prime(word)
    verify = sympy.isprime(proof // prime_private_word)
    return jsonify({"verify": verify})


@app.route("/batch", methods=["GET"])
def create_batch():
    # Read a list of proofs and a list of words and verify them
    proofs = request.args.get("proofs").split(",")
    words = request.args.get("words").split(",")
    for proof in proofs:
        proof = int(proof)
        for word in words:
            prime_private_word = deterministic_word_to_prime(word)
            verify = sympy.isprime(proof // prime_private_word)
            if verify:
                return jsonify({"verify": True})
    return jsonify({"verify": False})


@app.route("/")
def home():
    return """
    <html>
    <head><title>ZKP 4 LLMS</title></head>
    <body>
        <h1>ZKP 4 LLMS</h1>
        <p>Create a proof for the word "Hello": <a href="/proof?word=hello">[Try me]</a></p>
        <p>Verify that proof against the word "Bye": <a href="/verify?word=bye&proof=123">[Try me]</a></p>
        <p>Verify a batch of proofs against a batch of words: <a href="/batch?words=hello,world,how,are,you&proofs=123,456">[Try me]</a></p>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)
