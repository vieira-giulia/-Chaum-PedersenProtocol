import grpc
from concurrent import futures
#import threading
import proof_pb2
import proof_pb2_grpc
import numpy as np
import sympy
import parameters

#def generate_large_prime():
    # Generate random int32
    #candidate = np.random.randint(np.iinfo(np.int32).min, np.iinfo(np.int32).max + 1, dtype=np.int32)

    # Ensure the candidate is odd
    #candidate |= 1

    # Check if candidate is prime
    # Performing the Miller-Rabin primality test
    #while not sympy.isprime(candidate):
    #    candidate += 2

    #return candidate

#def find_primitive_root(q):
    # Find a primitive root modulo q
    # Generator of a group of order q
    #generator = np.random.randint(2, q)
    #while np.gcd(generator, q) != 1:
    #    generator = np.random.randint(2, q)
    #return generator

class ChaumPedersenServicer(proof_pb2_grpc.ChaumPedersenServiceServicer):
    def __init__(self) -> None:
        #self.q = generate_large_prime()
        #self.g = find_primitive_root(self.q)
        #self.h = find_primitive_root(self.q)
        #while self.h == self.g:
        #    self.h = find_primitive_root(self.q)
        print(f"Parameters: q = {parameters.p}, g = {parameters.g}, h = {parameters.h}")
        
        self.y1 = None
        self.y2 = None

        self.r1 = None
        self.r2 = None
        self.c = None

    #def Parameters(self, request, context):
    #    return proof_pb2.ParametersResponse(g=self.g, h=self.h, q=self.q)
    
    def Register(self, request, context):
        # Save registration
        self.y1 = sympy.Integer(request.y1)
        self.y2 = sympy.Integer(request.y2)
        print(f"Received registration: y1 = {self.y1}, y2 = {self.y2}")

        return proof_pb2.RegistrationResponse(success=True)

    def CommitmentChallenge(self, request, context):
        # Save commitment
        self.r1 = sympy.Integer(request.r1)
        self.r2 = sympy.Integer(request.r2)
        print(f"Received commitments: r1 = {self.r1}, r2 = {self.r2}")

        # Generate random value c as challenge
        self.c = sympy.Integer(np.random.randint(1, high=np.iinfo(np.int32).max, dtype=np.int32) % parameters.p)

        # Send challenge as commitment response
        print(f"Challenge sent: c = {str(self.c)}")
        return proof_pb2.CommitmentChallengeResponse(c=str(self.c))

    def VerifyProof(self, request, context):
        s = sympy.Integer(request.s)
        print(f"Verifying proof': {s}")
        a = sympy.Pow(parameters.g, s)
        print(f"a = {a}")
        b = sympy.Pow(self.y1, self.c)
        print(f"b = {b}")
        c = sympy.Pow(a,b)
        print(f"c = {c}")
        r1_verification = sympy.Mod(c, parameters.p)
        print(f"r1 = {r1_verification}")

        a = sympy.Pow(parameters.h, s)
        print(f"a = {a}")
        b = sympy.Pow(self.y2, self.c)
        print(f"b = {b}")
        c = sympy.Pow(a,b)
        print(f"c = {c}")
        r2_verification = sympy.Mod(c, parameters.p)
        print(f"r1 = {r2_verification}")


        #r1_verification = ((self.g ** s) % self.q) * ((self.y1 ** self.c) % self.q)  % self.q
        #r2_verification = ((self.h ** s)  % self.q ) * ((self.y2 ** self.c) % self.q)  % self.q
        print('r1 = {r1} = {r1_verification}')
        print('r2 = {r2} = {r2_verification}')

        # Verify proof
        if self.r1 == r1_verification and self.r2 == r2_verification:
            print('successful verification')
            return proof_pb2.VerifyProofResponse(success=True)
        else:
            print('failed verification')
            return proof_pb2.VerifyProofResponse(success=False)

def serve():
    #stop_event = threading.Event()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    proof_pb2_grpc.add_ChaumPedersenServiceServicer_to_server(ChaumPedersenServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()

    server.wait_for_termination()
    #stop_event.wait()
    #server.stop(grace=None)

if __name__ == '__main__':
    serve()
