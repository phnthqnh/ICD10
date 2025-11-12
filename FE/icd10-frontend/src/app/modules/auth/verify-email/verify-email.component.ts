import { Component, ViewEncapsulation } from '@angular/core';
import { RouterLink } from '@angular/router';
import { fuseAnimations } from '@fuse/animations';

@Component({
    selector     : 'auth-verify-email',
    templateUrl  : './verify-email.component.html',
    encapsulation: ViewEncapsulation.None,
    animations   : fuseAnimations,
    standalone   : true,
    imports      : [RouterLink],
})
export class AuthVerifyEmailComponent
{
    /**
     * Constructor
     */
    constructor()
    {
    }
}
