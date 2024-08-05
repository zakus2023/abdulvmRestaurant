
#this will be used to redirect the user to a specific dashboard based on the user role
def detectUser(user):
    if user.role == 1:
        redirectUrl = 'vendorDashboard'
        return redirectUrl
    
    elif user.role == 2:
        redirectUrl = 'custdashboard'
        return redirectUrl
    
    elif user.role == None and user.is_superadmin:
        redirectUrl = '/admin'
        return redirectUrl

    

    
    
        