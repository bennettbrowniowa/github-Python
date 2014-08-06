from __future__ import print_function
'''
Compare the files of two repos.
'''
import requests

##
# Authorization
##
token = '0...f'
import PRIVATEkeys
token = PRIVATEkeys.gitkey
key = {'Authorization':'token '+token}

#a = requests.get('https://api.github.com', headers=key)
#b = requests.get('https://api.github.com/user/repos', headers=key)

def get_repos():
    ''' Lists the organizational repos available to the key's owner
    returns a list of strings
    '''
    repos = requests.get('https://api.github.com/orgs/PLTWCS/repos', headers=key)
    names = []
    for repo in repos.json():
        names.append(repo['name'])
    return names

#print get_repos()


#cse1415 = requests.get('https://api.github.com/repos/PLTWCS/CSE/contents', headers=key)
#for i in cse1415.json():
#    print i['type'], i['name']
    

def get_repo_file_hashes(owner, repo):
    ''' Get all the sha1 hashes in the tree of the master head commit
    returns a list of (path, name, sha)
    '''
    #Get master head commit's tree sha
    master = requests.get('https://api.github.com/repos/'+owner+'/'+repo+'/branches/master', headers=key)
    master = master.json()
    head_tree_sha = master['commit']['commit']['tree']['sha']
    
    # Get all the hashes in that tree
    
    a_tree=[]
    return tree(owner, repo, head_tree_sha, '', a_tree) 

def tree(owner, repo, sha, path, list_so_far):
    '''appends the contents of tree specified by sha to list_so_far
    each file contained appended as (path, name, sha)
    returns a list of 3-tuples
    '''
    tree_contents = requests.get('https://api.github.com/repos/'+owner+'/'+repo+'/git/trees/'+sha, headers=key)
    tree_contents = tree_contents.json()
    try:
        a= tree_contents['tree']
    except KeyError:
        print ("error in tree(): ",tree_contents,owner,repo,sha)
    for item in tree_contents['tree']:
        if item['type']=='blob':
            new_tuple = (path+'/'+item['path'], item['path'], item['sha'])
            #print (new_tuple)
            list_so_far.append(new_tuple)     
        elif item['type']=='tree': 
            list_so_far = tree(owner, repo, item['sha'], path+'/'+item['path'], list_so_far)
        else:
            print("tree(): expected only blobs and trees."    )
    return list_so_far        
        

    
def make_dict(files):
    '''Converts a list of 3-tuples (path, name, sha) to dict
    Returns a dictionary {name: (sha, path)}, stripped of duplicates, git files, and uncompressed source files
    '''
    #make_dict() should be refactored into tree()
    filedict={}
    git = [] # Count 'em
    source = [] # Count them
    duplicates = []
    for f in files:
        # Get sha for each file
        path, name, sha = f
        
        if 'git' in name: # ignore git files
            git.append(path+name) # but track them
            print('git:'+path+name)
        else:
            ## # ignore uncompressed source files
            if 'esource' in name: 
                filename_derivative = ''.join(name.split('esource')) #chop out from Resource
            else:
                filename_derivative = name
            if ("ource" in path) and ("zip" not in filename_derivative): 
                source.append(path+name)
                print('source: '+path+name)
            else:    
                if filedict.has_key(name):# If the filename is duplicated, print a warning message
                    duplicates.extend(path+name)
                    print(name+" duplicated: \t"+path+" and \n\t\t\t"+filedict[name][1]+'\n')
                # Append the sha corresponding to that filename dict
                else:
                    filedict[name]=(sha, path)
                    
        
    return filedict



def compare_repos(a, b, a_name='cse_1314', b_name='cse_1415'):
    ''' Compares two repos
    a and b are dictionaries of file objects in a repo's tree.
    {name:(sha,path), ...}
    
    returns (same, output, no_exist) where
        same is an int
        output is a list of strings describing non-identical pairs
        no_exist is a list of strings describing files in cse_1415 but not in cse_1314
    '''
    same = 0 # Accumulate number of matching files
    output=[] # Aggregate files that do not match
    no_exist=[] # Aggregate files that do not exist in current repo
    
    afiles = a.keys()
    for filename in b:
        sha_b, path_b = b[filename]
        try:
            # Compare to the current version
            sha_a, path_a = a[filename]
            # If that didn't brnach to except,
            # filename is also in a
            if sha_b == sha_a:
                same +=1 # Count the matching versions
                afiles.remove(filename)
            else:
                output.append(filename + ' \tis different in '+ a_name + '(' + sha_a[:6] + ') & ' + b_name + '('+sha_b[:5]+').')
        except KeyError:
            no_exist.append(filename + " \tdoes not exist in " + a_name )
        
    print(str(same)+" files were the same in the two repos.")  
    return same, output, no_exist

    
def get_commit_path(owner, repo, file_sha):
    '''
    if the file_sha is in the repo, return a list of commits from the master head backwards which updated that file.
    '''
    commit_list = []
    commit_list.append(commit_sha, file_sha, commit_message, commit_notes)
    # not yet done here. :-)
    return commit_list
        
refresh=True
if refresh:
    cse_1314 = []
    for lesson in ['1-1','1-2','1-3','1-4','1-5','2-1','2-2','2-3','3-1','3-2','4-1','4-2']:
        cse_1314.extend(get_repo_file_hashes('PLTWCS', 'CSE-'+lesson))
    cse_1415 = get_repo_file_hashes('PLTWCS', 'CSE')    
    cse_1415 = make_dict(cse_1415)
    cse_1314= make_dict(cse_1314)


same, different, no_exist = compare_repos(cse_1314, cse_1415, a_name='cse_1314', b_name='cse_1415')
print('same, len(different), len(no_exist):')
print(same, len(different), len(no_exist), 'totals '+str(same + len(different) + len(no_exist)), sep=', ')

    