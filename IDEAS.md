Ideas for Bolt
==============

# Global fabric file #

It would be awesome to have a global `fabfile.py` but allow namespaces
to be rejected and hidden from sight within particular projects and
subnets.

## Namespace restriction/specification ##

**Current Tasks**

    t                                     Set the execution target. See README for syntax.
    target                                Set the execution target. See README for syntax.
    bs.apps.atlas.deploy                  Deploy a branch and any environment overrides to an atlas node
    bs.apps.bolt.dump_hosts               Generate a data fixture of nodes
    bs.apps.bolt.load_hosts_fixture       Load the hosts fixture into bolt
    bs.apps.bolt.reload                   Get hosts from EC2 and load them as a fixture
    bs.apps.common.environment_overrides  Change the deployment overrides given
    bs.apps.common.get_node               Get the first matching node based on a search of host_string*
    bs.apps.common.set_branch             Set the branch override
    bs.apps.cp.deploy                     Deploy an update to customer portal
    bs.apps.cp.deployed_branch            Get deployed branch of customer portal
    bs.apps.cp.deployed_version           Get deployed revision of customer portal
    bs.apps.pipeline.deploy_ami           Given an AMI version, subnet, and some other info, deploy a cluster
    bs.apps.pipeline.restart_hbase        Restart the hbase service
    bs.chef.node.get_node                 Get the first matching node based on a search of host_string*
    bs.ec2.roles.clcache                  Invalidate the role/hosts cache
    bs.knife.ami_create                   Build an AMI for given profile, ami version and package set
    bs.knife.do                           Run `knife` command either locally or on a remote host
    bs.knife.ebs_list                     `knife bs ebs list ame1.<subnet>`
    bs.knife.server_create                `knife bs server create <args> <kwargs>`
    bs.knife.server_list                  `knife bs server list ame1.<subnet>`
    bs.system.restart                     Reboot the host
    bs.system.uname                       Get uname information about the host

The idea is then to do two things:

  1. Allow common tasks to be visible
  2. Hide tasks that don't apply to profile

This way, `bs.apps` can be specified as the Profile root, and profiles
below that are not part of a `pertinent` spec.

*The question becomes: where to store all this info?*

It would be nice to define it in a YAML spec that gets reloaded on
`management` command execution, which can even be done from within Bolt
under the Bolt project.

# atlas.yaml #

It would be great if we could integrate Bolt with our atlas.yaml
entirely, giving us environments, subnets, profiles and stacks.

## Navigation ##

From the front page, you can select a project, then an environment, then
drill down to the vpc, then the subnet, with shortcuts to frequently
accessed items available per user.

## Project page ##

The project page should provide

  - Short description of the project
  - Get rid of project type
  - Map to profiles in YAML**[1]**
    - This sets a filter on which instances can be selected by tasks
      within that Project.
    - Do not make this a requirement, however. A Project can exist
      outside of the confines of profiles.

## Role builder ##

The role builder has already been partially implemented via `roles.py`
in the fabric repo. However it would be nice if this was a more generic
library for building roles that involves inclusion - select multiple
subnets - and exclusion - restricting by profile.

It gathers data from `EC2` and the `chef server`**[2]** to build up a
set of roles. A role is a selector either of `restrictor` or `extender`
type. These are defined below.

**[2]**

### Build process ###

The UI for fabric bolt should allow executing a task on multiple hosts
of the same profile, or without any profile restriction.

#### Selectors ####

Selectors should exist for every `role` type that can be created. For
instance, each profile comprises a `role` (set of hosts). Each subnet
specifies a set of hosts and therefore is also a role.

Note that a `restrictor` without any `extenders` also acts as a
`extender`. This is so you can specify a task to run on all hosts of a
given `profile`.

##### Restrict #####

A restriction selector can be used to restrict which roles are able to
use this task. It is effectively used to apply a set union with any
extensions applied.

    profile
    stack

##### Extend #####

An extension selector is used to add possible hosts for execution. For
instance, selecting a subnet includes a bunch of heterogenous host
types/profiles. An `stg1` specification will likely include a
`customer-portal`, `entity-management` and `slave`/`master` nodes. If
unrestricted using a restriction selector, the specified task will run
on all of the nodes.

    environment
    subnet

#### Example ####

##### Selectors #####

(**extender**) *tst1 subnet* 

    "s.tst1": [
        "rs104.tst1.ame1.bitsighttech.com", 
        "rs103.tst1.ame1.bitsighttech.com", 
        "cm101.tst1.ame1.bitsighttech.com", 
        "rs101.tst1.ame1.bitsighttech.com", 
        "rs106.tst1.ame1.bitsighttech.com", 
        "rs102.tst1.ame1.bitsighttech.com", 
        "rs109.tst1.ame1.bitsighttech.com", 
        "rs107.tst1.ame1.bitsighttech.com", 
        "cp101.tst1.ame1.bitsighttech.com", 
        "em101.tst1.ame1.bitsighttech.com", 
        "rs108.tst1.ame1.bitsighttech.com", 
        "ms101.tst1.ame1.bitsighttech.com", 
        "rs105.tst1.ame1.bitsighttech.com", 
        "kb101.tst1.ame1.bitsighttech.com"
    ], 

(**extender**) *prd1 subnet*

    "s.prd1": [
        "rs106.prd1.ame1.bitsighttech.com", 
        "rs101.prd1.ame1.bitsighttech.com", 
        "em101.prd1.ame1.bitsighttech.com", 
        "rs103.prd1.ame1.bitsighttech.com", 
        "kb101.prd1.ame1.bitsighttech.com", 
        "rs109.prd1.ame1.bitsighttech.com", 
        "rs102.prd1.ame1.bitsighttech.com", 
        "rs105.prd1.ame1.bitsighttech.com", 
        "ms101.prd1.ame1.bitsighttech.com", 
        "cm101.prd1.ame1.bitsighttech.com", 
        "rs108.prd1.ame1.bitsighttech.com", 
        "rs104.prd1.ame1.bitsighttech.com", 
        "rs107.prd1.ame1.bitsighttech.com"
    ], 

(**restrictor**) *entity-mgr profile*

    "p.entity-mgr": [
        "em101.prd1.ame1.bitsighttech.com", 
        "em101.stg1.ame1.bitsighttech.com", 
        "em101.dev1.ame1.bitsighttech.com", 
        "em101.tst1.ame1.bitsighttech.com", 
        "entity-mgr.stg1.ame1.bitsighttech.com", 
        "em101.dev2.ame1.bitsighttech.com"
    ], 

##### Resulting host list #####

`(s.tst1 ∪ s.prd1) ∩ p.entity-mgr`

    env.hosts: [
        "em101.tst1.ame1.bitsighttech.com", 
        "em101.prd1.ame1.bitsighttech.com", 
    ]
