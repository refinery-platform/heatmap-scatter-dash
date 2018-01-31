# Quick first-time start-up and scalability are contradictory requirements

I've come to believe that looking for one technology to give us quick
first-time startup and scalability (and to do it efficiency) is not going
to be successful. Quick startup will generally require some kind of over-provisioning,
while scalable solutions will generally require more up-front investment.

This isn't the end of the world: I could imagine Refinery visualizations where they come in pairs,
and the user needs to choose between having something come up fast, or having something that is more durable.
I'm still exploring, but right now Elastic Beanstalk seems like the best option

## Criteria

- Builds on existing django-docker?
- Just weird?
- Cost?
- Scalable: multiple users on same visualization?
- Scalable: multiple users on different visualizations?
- Learning curve?
- Likelihood of success?
- Vendor lock in?
- Core could run independently of Refinery?

## Preferred Tech

### [AWS: Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/) (Python)

It's successfully running with `--demo` right now, so I think I should invest more time here.
The initial build takes some time. I also needed to add some python code to match
the end-points they expected: There's very little required configuration...
but more reliance on convention.

### [AWS: Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/) (Docker)

At least for now, working at the Python layer seems to introduce fewer variables,
but once that's sorted out, I could imagine switching up to Docker, so that there's
less variation between the stacks.

## Other Tech

### Galaxy

Could imagine a Galaxy workflow which starts up a webserver, and second process
which just waits for *x* minutes of inactivity before returning a 0-status.

Trying to expose a port from inside Galaxy might not work at all, and even if it did,
Galaxy is not designed for things to start up immediately, and the server would also
necessarily shut down after some finite period of time.

### [Zappa](https://github.com/Miserlou/Zappa)

Zappa is plausible, but the first launch is going to be very slow because it's
bundling all dependencies and sending them to S3. Successive loads could be fast...
if the server starts up quickly; If the app has a lot of in-memory state (instead
of pulling from a DB each time) then that initialization will be repeated
on each request.

I also have some concerns about easy of use: I went through several cycles of 
whack-a-mole, and I might have been getting closer, but rebuilding the bundles
with each tweak was a slow process. It might be lot less painful on a project
with fewer, smaller, dependencies.

Zappa is Python-specific, though the serverless philosophy has been implemented
for multiple languages.

### [django-wsgi](https://pythonhosted.org/django-wsgi/)

This is an interesting small library that seems to do for any python web app
what django-docker does for docker. That said, it wasn't obvious how to add
apps at run time, rather than specifying them in code. I'd like to keep this in
mind, though: all of these other approaches have so much overhead, and if we
just want to run one webapp inside another it can be done more easily.
(... at the cost of isolation and language and version independence.)

### non-local Docker Engine

It should be fairly straight-forward just to have a separate burstable instance
where Docker Engine runs. This gives us some scalability, but we'll still need
to time out and restart the instances. This also doesn't give us any leverage 
for helping core start visualizations outside Refinery.

### AWS: [Fargate](https://aws.amazon.com/fargate/) / [EKS](https://aws.amazon.com/eks/) / [ECS](https://aws.amazon.com/ecs/)

I feel like these should be viable if we're already building from Docker. I spent
some time with Fargate, and it might be worthwhile to try again. If it did work,
I'm not sure what the advantage would be over Elastic Beanstalk for Docker.