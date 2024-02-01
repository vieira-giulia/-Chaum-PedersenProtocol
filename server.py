import grpc
from concurrent import futures
import proof_pb2
import proof_pb2_grpc
import numpy as np
import sympy

def generate_large_prime():
    # Generate random int32
    candidate = np.random.randint(np.iinfo(np.int32).min, np.iinfo(np.int32).max + 1, dtype=np.int32)

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
        self.q = generate_large_prime()

        # Find g and h using q
        self.g = find_primitive_root(self.q)
        self.h = find_primitive_root(self.q)

        self.client_y1 = None
        self.client_y2 = None

        self.r1 = None
        self.r2 = None

    def Parameters(self, request, context):
        return proof_pb2.ParametersResponse(g=self.g, h=self.h, q=self.q)
    
    def Register(self, request, context):
        # Save registration
        if request.y1 and request.y2:
            self.client_y1 = request.y1
            self.clien_y2 = request.y2

            print(f"Received registration: y1={self.client_y1}, y2={self.client_y2}")
            return proof_pb2.RegistrationResponse(success=True)
        else:
            print('ERROR')
            return proof_pb2.RegistrationResponse(success=False)


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

        if self.client_y1 is None or self.client_y2 is None:
            return proof_pb2.LoginResponse(success=False, message='not registered')
        
        # Verify proof
        verification = (self.r1 == (self.g**s)*(self.y1**self.c) 
                        and self.r2 == (self.h**s)(self.y2**self.c))

        return proof_pb2.LoginResponse(success=verification, message='yay')

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    proof_pb2_grpc.add_ChaumPedersenServiceServicer_to_server(ChaumPedersenServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
