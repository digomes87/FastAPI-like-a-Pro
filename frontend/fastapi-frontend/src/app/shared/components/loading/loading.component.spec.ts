import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { LoadingComponent } from './loading.component';
import { LoadingService } from '../../../core/services/loading.service';
import { BehaviorSubject } from 'rxjs';

describe('LoadingComponent', () => {
  let component: LoadingComponent;
  let fixture: ComponentFixture<LoadingComponent>;
  let loadingService: jasmine.SpyObj<LoadingService>;
  let loadingSubject: BehaviorSubject<boolean>;

  beforeEach(async () => {
    loadingSubject = new BehaviorSubject<boolean>(false);
    const loadingServiceSpy = jasmine.createSpyObj('LoadingService', ['setLoading'], {
      loading$: loadingSubject.asObservable()
    });

    await TestBed.configureTestingModule({
      declarations: [LoadingComponent],
      imports: [MatProgressSpinnerModule],
      providers: [
        { provide: LoadingService, useValue: loadingServiceSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(LoadingComponent);
    component = fixture.componentInstance;
    loadingService = TestBed.inject(LoadingService) as jasmine.SpyObj<LoadingService>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should show loading when service emits true', () => {
    loadingSubject.next(true);
    fixture.detectChanges();
    
    expect(component.isLoading).toBe(true);
    const loadingOverlay = fixture.nativeElement.querySelector('.loading-overlay');
    expect(loadingOverlay).toBeTruthy();
  });

  it('should hide loading when service emits false', () => {
    loadingSubject.next(false);
    fixture.detectChanges();
    
    expect(component.isLoading).toBe(false);
    const loadingOverlay = fixture.nativeElement.querySelector('.loading-overlay');
    expect(loadingOverlay).toBeFalsy();
  });
});