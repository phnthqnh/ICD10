import { Location, NgIf } from '@angular/common';
import {
    ChangeDetectorRef,
    Component,
    OnDestroy,
    ViewEncapsulation,
} from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { FuseLoadingBarComponent } from '@fuse/components/loading-bar';
import { Subject } from 'rxjs';
import { LanguagesComponent } from '../../common/languages/languages.component';
import { SharedModule } from 'app/shared/shared.module';
import { AuthLayoutService } from 'app/core/auth/auth-layout.service';
import { GlobalAlertComponent } from '../../common/global-alert/global-alert.component';

@Component({
    selector: 'auth-layout',
    templateUrl: './auth.component.html',
    encapsulation: ViewEncapsulation.None,
    standalone: true,
    imports: [
        FuseLoadingBarComponent,
        NgIf,
        LanguagesComponent,
        SharedModule,
        RouterOutlet,
        GlobalAlertComponent,
    ],
})
export class AuthLayoutComponent implements OnDestroy {
    private _unsubscribeAll: Subject<any> = new Subject<any>();

    /**
     * Constructor
     */
    constructor(
        private _router: Router,
        private _location: Location,
        public _authLayoutService: AuthLayoutService,
        private cdr: ChangeDetectorRef
    ) {}

    // -----------------------------------------------------------------------------------------------------
    // @ Lifecycle hooks
    // ------
    // -----------------------------------------------------------------------------------------------

    ngOnInit(): void {
        this._authLayoutService.title$.subscribe(() => {
            this.cdr.detectChanges();
        });

        this._authLayoutService.titleDes$.subscribe(() => {
            this.cdr.detectChanges();
        });
        this._authLayoutService.image$.subscribe(() => {
            this.cdr.detectChanges();
        });
    }
    /**
     * On destroy
     */
    ngOnDestroy(): void {
        // Unsubscribe from all subscriptions
        this._unsubscribeAll.next(null);
        this._unsubscribeAll.complete();
    }
    isSignInPage(): boolean {
        const urlSignIn = this._router.url.split('?')[0];
        return urlSignIn === '/sign-in';
    }

    goBack(): void {
        this._location.back();
    }
}
