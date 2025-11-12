import { Component, ViewEncapsulation } from '@angular/core';
import { RouterLink } from '@angular/router';
import { fuseAnimations } from '@fuse/animations';

@Component({
    selector     : 'auth-not-verify-email',
    templateUrl  : './not-verify-email.component.html',
    encapsulation: ViewEncapsulation.None,
    animations   : fuseAnimations,
    standalone   : true,
    imports      : [RouterLink],
})
export class AuthNotVerifyEmailComponent
{
    /**
     * Constructor
     */
    constructor()
    {
    }
}
