import grpc
from concurrent import futures
import proof_pb2
import proof_pb2_grpc
import numpy as np
import sympy

def generate_large_prime():
    # Set the bit length for a large prime
    bit_length = 1024

    # Generate a random number with the specified bit length
    candidate = np.random.get_state()[1][0] % (2**(bit_length - 1))

    # Ensure the candidate is odd
    candidate |= 1

    # Check if candidate is prime
    # Performing the Miller-Rabin primality test
    while not sympy.isprime(candidate):
        candidate += 2

    return candidate

def find_primitive_root(q):
    # Find a primitive root modulo q
    # Generator of a group of order q
    generator = np.random.randint(2, q)
    while np.gcd(generator, q) != 1:
        generator = np.random.randint(2, q)
    return generator

class ChaumPedersenServicer(proof_pb2_grpc.ChaumPedersenServiceServicer):
    def __init__(self) -> None:
        # Generate a large random prime number for q
        q = generate_large_prime()

        # Find g and h using q
        g = find_primitive_root(q)
        h = find_primitive_root(q)

    def Parameters(self, request, context):
        return proof_pb2.ParametersResponse(g=self.g, h=self.h, q=self.q)
    
    def Register(self, request, context):
        # Save registration
        self.client_y1 = request.y1
        self.clien_y2 = request.y2

        print(f"Received registration: y1={self.y1}, y2={self.y2}")

        return proof_pb2.RegistrationResponse(success=True)


    def CommitmentChallenge(self, request, context):
        # Save commitment
        self.r1 = request.r1
        self.r2 = request.r2

        # Generate random value c as challenge
        self.c = np.random.randint(np.iinfo(np.int32).min, np.iinfo(np.int32).max)

        # Send challenge as commitment response
        return proof_pb2.CommitmentResponse(c=self.c)

    def VerifiyProof(self, request, context):
        # Save proof
        s = request.s

        # Verify proof
        verification = (self.r1 == (self.g**s)*(self.y1**self.c) 
                        and self.r2 == (self.h**s)(self.y2**self.c))

        return proof_pb2.LoginResponse(success=verification)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    proof_pb2_grpc.add_ChaumPedersenServiceServicer_to_server(ChaumPedersenServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
